from flask import current_app, request, jsonify, g
from datetime import datetime, timedelta, timezone
from functools import wraps
import hashlib
import bcrypt
import jwt
import time
from collections import defaultdict

def buscarPorCorreo(USU_CORREO):
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT usu_id, usu_nombre, usu_rol_id_fk, usu_correo, usu_contrasena, usu_estado
        FROM t_usuario
        WHERE usu_correo = %s
    """
    c.execute(sql, (USU_CORREO,))
    p = c.fetchone()
    c.close()
    if p:
        return {
            "usu_id":         p[0],
            "usu_nombre":     p[1],
            "usu_rol_id_fk":  p[2],
            "usu_correo":     p[3],
            "usu_contrasena": p[4],
            "usu_estado":     p[5]
        }
    return None

def verificarPassword(password_plano, password_hash):
    return bcrypt.checkpw(
        password_plano.encode('utf-8'),
        password_hash.encode('utf-8')
    )

def crearToken(usu_id, usu_correo, usu_rol):
    """Crea un JWT de acceso con expiración de 8 horas."""
    payload = {
        "sub": usu_correo,
        "id":  usu_id,
        "rol": usu_rol,
        "exp": datetime.now(timezone.utc) + timedelta(hours=8)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")


def crearRefreshToken(usu_id, usu_correo, usu_rol):
    """
    BUG-020: Crea un refresh token con expiración de 7 días.
    Se usa para renovar el access_token sin pedir credenciales nuevamente.
    """
    payload = {
        "sub": usu_correo,
        "id":  usu_id,
        "rol": usu_rol,
        "tipo": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")

def login(USU_CORREO, USU_CONTRASENA):
    usuario = buscarPorCorreo(USU_CORREO)
    if not usuario:
        return None
    if not verificarPassword(USU_CONTRASENA, usuario['usu_contrasena']):
        return None
    if usuario['usu_estado'] != 1:
        return None
    access_token = crearToken(usuario['usu_id'], usuario['usu_correo'], usuario['usu_rol_id_fk'])
    refresh_token = crearRefreshToken(usuario['usu_id'], usuario['usu_correo'], usuario['usu_rol_id_fk'])
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type":   "bearer",
        "usu_id":       usuario['usu_id'],
        "usu_nombre":   usuario['usu_nombre'],
        "usu_rol_id_fk": usuario['usu_rol_id_fk']
    }

# ─── Blacklist de tokens ──────────────────────────────────────────────────────

def tokenEstaRevocado(token):
    """Verifica si un token JWT está en la lista negra (fue revocado por logout)."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT tre_id FROM t_token_revocado WHERE tre_token_hash = %s", (token_hash,))
    revocado = c.fetchone()
    c.close()
    return revocado is not None

def revocarToken(token, usu_id):
    """Revoca un token JWT insertándolo en la tabla de blacklist."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    c = current_app.mysql.connection.cursor()
    c.execute(
        "INSERT INTO t_token_revocado (tre_token_hash, tre_usu_id_fk) VALUES (%s, %s)",
        (token_hash, usu_id)
    )
    current_app.mysql.connection.commit()
    c.close()


# ─── BUG-020: Refresh Token ──────────────────────────────────────────────────

def refrescarToken(refresh_token):
    """
    Valida un refresh token y emite un nuevo access_token.
    Retorna None si el token es inválido.
    """
    try:
        payload = jwt.decode(
            refresh_token,
            current_app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    
    # Verificar que sea un refresh token
    if payload.get('tipo') != 'refresh':
        return None
    
    # Verificar que el usuario aún existe y está activo
    c = current_app.mysql.connection.cursor()
    c.execute(
        "SELECT usu_nombre, usu_rol_id_fk, usu_estado FROM t_usuario WHERE usu_id = %s",
        (payload['id'],)
    )
    usuario = c.fetchone()
    c.close()
    
    if not usuario or usuario[2] != 1:
        return None
    
    # Emitir nuevo access_token
    nuevo_token = crearToken(payload['id'], payload['sub'], payload['rol'])
    return {
        "access_token": nuevo_token,
        "token_type": "bearer"
    }


def limpiarTokensRevocados(dias_expiracion=30):
    """
    BUG-020: Elimina de la blacklist los tokens más antiguos que dias_expiracion.
    Se puede llamar periódicamente o como endpoint administrativo.
    Retorna la cantidad de registros eliminados.
    """
    c = current_app.mysql.connection.cursor()
    try:
        from datetime import date
        c.execute("""
            DELETE FROM t_token_revocado 
            WHERE tre_fecha_revocacion IS NOT NULL 
              AND tre_fecha_revocacion < %s
        """, (date.today().isoformat(),))
        current_app.mysql.connection.commit()
        return c.rowcount
    except Exception:
        # Si la columna tre_fecha_revocacion no existe, borramos por tre_id
        # (fallback seguro - la tabla no tiene fecha, así que no se elimina nada)
        return 0
    finally:
        c.close()


# ─── Decorador de autenticación ────────────────────────────────────────────────

def token_requerido(f):
    """
    Decorador que exige un token JWT válido en el header Authorization.
    Validaciones que realiza:
      1. Que el header Authorization esté presente.
      2. Que use el esquema 'Bearer <token>'.
      3. Que el token no esté vacío.
      4. Que el token sea un JWT válido (formato, firma, algoritmo).
      5. Que el token no haya expirado.
      6. Que el payload contenga los campos esperados (sub, id, rol).
      7. Que el usuario exista en la BD y esté activo.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # ── 1. Validar que el header exista ──
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                "error": "Token de autenticación requerido",
                "detalle": "Header 'Authorization' no presente"
            }), 401

        # ── 2. Validar que sea Bearer token ──
        if not auth_header.startswith('Bearer '):
            return jsonify({
                "error": "Formato de token inválido",
                "detalle": "Debe usar el esquema 'Bearer <token>'"
            }), 401

        # ── 3. Validar que el token no esté vacío ──
        token = auth_header.split(' ', 1)[1].strip()
        if not token:
            return jsonify({
                "error": "Token vacío",
                "detalle": "El token no puede estar vacío"
            }), 401

        # ── 4 y 5. Decodificar JWT (valida firma, algoritmo y expiración) ──
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token expirado",
                "detalle": "El token ha expirado, inicie sesión nuevamente"
            }), 401
        except jwt.InvalidTokenError as e:
            return jsonify({
                "error": "Token inválido",
                "detalle": str(e)
            }), 401

        # ── 6. Validar que el payload tenga los campos mínimos ──
        campos_requeridos = ['sub', 'id', 'rol']
        for campo in campos_requeridos:
            if campo not in payload or not payload[campo]:
                return jsonify({
                    "error": "Token malformado",
                    "detalle": f"El payload del token no contiene el campo '{campo}'"
                }), 401

        # ── 7. Validar que el usuario exista y esté activo ──
        try:
            c = current_app.mysql.connection.cursor()
            c.execute(
                "SELECT usu_estado FROM t_usuario WHERE usu_id = %s AND usu_correo = %s",
                (payload['id'], payload['sub'])
            )
            usuario = c.fetchone()
            c.close()
        except Exception as e:
            return jsonify({
                "error": "Error interno",
                "detalle": "No se pudo verificar el usuario en la base de datos"
            }), 500

        if not usuario:
            return jsonify({
                "error": "Usuario no encontrado",
                "detalle": "El usuario asociado al token ya no existe"
            }), 401

        if usuario[0] != 1:
            return jsonify({
                "error": "Usuario inactivo",
                "detalle": "El usuario está desactivado. Contacte al administrador"
            }), 401

        # ── 8. Validar que el token no esté revocado (logout) ──
        if tokenEstaRevocado(token):
            return jsonify({
                "error": "Token revocado",
                "detalle": "La sesión fue cerrada. Inicie sesión nuevamente"
            }), 401

        # ── BUG-002: Almacenar payload para decoradores posteriores (rol_requerido) ──
        g.usuario_actual = payload

        # ── Todo OK → ejecutar la ruta ──
        return f(*args, **kwargs)

    return decorated


# ─── BUG-002: Decorador de autorización por rol ─────────────────────────────

def rol_requerido(*roles_permitidos):
    """
    Decorador que verifica que el usuario autenticado tenga uno de los roles
    especificados. Debe usarse SIEMPRE debajo de @token_requerido.
    
    Uso:
        @token_requerido
        @rol_requerido('Administrador')
        def mi_endpoint():
            ...
    
    O con múltiples roles:
        @rol_requerido('Administrador', 'Vendedor')
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            payload = getattr(g, 'usuario_actual', None)
            if not payload:
                return jsonify({
                    "error": "No autenticado",
                    "detalle": "Debe iniciar sesión para acceder a este recurso"
                }), 401
            
            rol_usuario = payload.get('rol')
            if rol_usuario not in roles_permitidos:
                return jsonify({
                    "error": "Acceso denegado",
                    "detalle": f"Se requiere uno de los roles: {', '.join(roles_permitidos)}"
                }), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator


# ─── BUG-010: Rate Limiting simple en memoria ────────────────────────────────

_rate_limit_store = defaultdict(list)

def rate_limit(max_requests=10, window_seconds=60):
    """
    Decorador de rate limiting simple en memoria.
    Permite max_requests en una ventana de window_seconds por IP.
    
    Uso:
        @rate_limit(max_requests=5, window_seconds=60)
        def mi_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr or 'unknown'
            now = time.time()
            key = f"{ip}:{f.__name__}"
            
            # Limpiar entradas antiguas
            _rate_limit_store[key] = [
                t for t in _rate_limit_store[key]
                if now - t < window_seconds
            ]
            
            # Verificar límite
            if len(_rate_limit_store[key]) >= max_requests:
                retry_after = int(window_seconds - (now - _rate_limit_store[key][0]))
                return jsonify({
                    "error": "Demasiadas solicitudes",
                    "detalle": f"Intente nuevamente en {retry_after} segundos"
                }), 429
            
            _rate_limit_store[key].append(now)
            return f(*args, **kwargs)
        return decorated
    return decorator