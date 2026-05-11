from flask import current_app, request, jsonify
from datetime import datetime, timedelta
from functools import wraps
import bcrypt
import jwt

def buscarPorCorreo(USU_CORREO):
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT usu_id, usu_nombre, usu_rol, usu_correo, usu_contrasena, usu_estado
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
            "usu_rol":        p[2],
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
    print("SECRET_KEY:", current_app.config['SECRET_KEY'])  # ← agrega esto
    payload = {
        "sub": usu_correo,
        "id":  usu_id,
        "rol": usu_rol,
        "exp": datetime.utcnow() + timedelta(hours=8)
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
    token = crearToken(usuario['usu_id'], usuario['usu_correo'], usuario['usu_rol'])
    return {
        "access_token": token,
        "token_type":   "bearer",
        "usu_nombre":   usuario['usu_nombre'],
        "usu_rol":      usuario['usu_rol']
    }

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

        # ── Todo OK → ejecutar la ruta ──
        return f(*args, **kwargs)

    return decorated