from flask import current_app
from models.usuarios_model import usuarios
from utils.search_builder import SearchBuilder
import bcrypt

def listarUsuarios(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_usuario',
        search_fields=['usu_id', 'usu_nombre', 'usu_correo', 't_rol.rol_nombre'],
        exact_fields=['usu_estado'],
        default_order='usu_nombre ASC',
        join_clause='LEFT JOIN t_rol ON t_usuario.usu_rol_id_fk = t_rol.rol_id',
        select_columns='t_usuario.*, t_rol.rol_nombre'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        u = usuarios(
            usu_id=item['usu_id'],
            usu_nombre=item['usu_nombre'],
            usu_rol=item.get('rol_nombre') or item.get('usu_rol_id_fk', ''),
            usu_correo=item['usu_correo'],
            usu_contrasena=item['usu_contrasena'],
            usu_estado=item['usu_estado'],
            usu_ultimo_acceso=item.get('usu_ultimo_acceso')
        ).todic()
        lista.append(u)

    result['data'] = lista
    return result


def _resolver_rol(nombre_rol):
    """Convierte nombre de rol ('Administrador') a código ('ROL001'). Crea el rol si no existe."""
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT rol_id FROM t_rol WHERE rol_nombre = %s", (nombre_rol,))
    row = c.fetchone()
    if row:
        c.close()
        return row[0]
    # Auto-crear el rol si no existe
    c.execute("SELECT MAX(rol_id) FROM t_rol")
    max_row = c.fetchone()
    next_num = 1
    if max_row and max_row[0]:
        try:
            next_num = int(max_row[0].replace('ROL', '')) + 1
        except (ValueError, TypeError):
            next_num = 1
    new_id = f"ROL{next_num:03d}"
    c.execute("INSERT INTO t_rol (rol_id, rol_nombre, rol_descripcion) VALUES (%s, %s, %s)",
              (new_id, nombre_rol, f'Rol {nombre_rol} (auto-creado)'))
    current_app.mysql.connection.commit()
    c.close()
    return new_id


def registrarUsuarios(USU_ID, USU_NOMBRE, USU_ROL, USU_CORREO, USU_CONTRASENA, USU_ESTADO, USU_ULTIMO_ACCESO):
    # BUG-003: Hashear contraseña antes de guardar
    contrasena_hash = bcrypt.hashpw(
        USU_CONTRASENA.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    # Resolver nombre de rol a código (ej: 'Administrador' → 'ROL001')
    rol_codigo = _resolver_rol(USU_ROL)
    c = current_app.mysql.connection.cursor()
    sql = """
        INSERT INTO t_usuario (usu_id, usu_nombre, usu_rol_id_fk, usu_correo, usu_contrasena, usu_estado, usu_ultimo_acceso) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    c.execute(sql, (USU_ID, USU_NOMBRE, rol_codigo, USU_CORREO, contrasena_hash, USU_ESTADO, USU_ULTIMO_ACCESO))
    current_app.mysql.connection.commit()
    id = c.lastrowid
    c.close()
    return usuarios(USU_ID, USU_NOMBRE, USU_ROL, USU_CORREO, USU_CONTRASENA, USU_ESTADO, USU_ULTIMO_ACCESO).todic()


def editarUsuarios(USU_ID, USU_NOMBRE, USU_ROL, USU_CORREO, USU_CONTRASENA, USU_ESTADO, USU_ULTIMO_ACCESO):
    # Resolver nombre de rol a código (ej: 'Administrador' → 'ROL001')
    rol_codigo = _resolver_rol(USU_ROL)
    c = current_app.mysql.connection.cursor()
    
    # Si no se envía contraseña (es None o vacía), mantener la actual
    if USU_CONTRASENA and USU_CONTRASENA.strip() != '':
        if not USU_CONTRASENA.startswith('$2b$') and not USU_CONTRASENA.startswith('$2a$'):
            contrasena_hash = bcrypt.hashpw(
                USU_CONTRASENA.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
        else:
            contrasena_hash = USU_CONTRASENA
        
        sql = """
            UPDATE t_usuario 
            SET usu_nombre=%s, usu_rol_id_fk=%s, usu_correo=%s, usu_contrasena=%s, usu_estado=%s, usu_ultimo_acceso=%s
            WHERE usu_id=%s
        """
        c.execute(sql, (USU_NOMBRE, rol_codigo, USU_CORREO, contrasena_hash, USU_ESTADO, USU_ULTIMO_ACCESO, USU_ID))
    else:
        # No cambiar la contraseña
        sql = """
            UPDATE t_usuario 
            SET usu_nombre=%s, usu_rol_id_fk=%s, usu_correo=%s, usu_estado=%s, usu_ultimo_acceso=%s
            WHERE usu_id=%s
        """
        c.execute(sql, (USU_NOMBRE, rol_codigo, USU_CORREO, USU_ESTADO, USU_ULTIMO_ACCESO, USU_ID))
    
    current_app.mysql.connection.commit()
    c.close()
    return usuarios(USU_ID, USU_NOMBRE, USU_ROL, USU_CORREO, USU_CONTRASENA, USU_ESTADO, USU_ULTIMO_ACCESO).todic()


def eliminarUsuarios(USU_ID):
    c = current_app.mysql.connection.cursor()
    
    # Verificar dependencias antes de eliminar
    dependencias = []

    # Obtener el rol del usuario
    c.execute("SELECT usu_rol_id_fk FROM t_usuario WHERE usu_id = %s", (USU_ID,))
    row_rol = c.fetchone()
    rol_usuario = row_rol[0] if row_rol else None

    # Verificar si es el último usuario con ese rol (FK constraint t_rol → t_usuario)
    if rol_usuario:
        c.execute("SELECT COUNT(*) FROM t_usuario WHERE usu_rol_id_fk = %s AND usu_id != %s", (rol_usuario, USU_ID))
        if c.fetchone()[0] == 0:
            dependencias.append(f"rol '{rol_usuario}' (es el único usuario con ese rol)")

    c.execute("SELECT COUNT(*) FROM t_pedido WHERE ped_usu_id_fk = %s", (USU_ID,))
    if c.fetchone()[0] > 0:
        dependencias.append("pedidos")
    c.execute("SELECT COUNT(*) FROM t_compra WHERE com_usu_id_fk = %s", (USU_ID,))
    if c.fetchone()[0] > 0:
        dependencias.append("compras")
    try:
        c.execute("SELECT COUNT(*) FROM t_factura WHERE fac_usu_id_fk = %s", (USU_ID,))
        if c.fetchone()[0] > 0:
            dependencias.append("facturas")
    except Exception:
        pass
    try:
        c.execute("SELECT COUNT(*) FROM t_devolucion WHERE dev_usu_id_fk = %s", (USU_ID,))
        if c.fetchone()[0] > 0:
            dependencias.append("devoluciones")
    except Exception:
        pass
    try:
        c.execute("SELECT COUNT(*) FROM t_monitoria WHERE mon_usu_id_fk = %s", (USU_ID,))
        if c.fetchone()[0] > 0:
            dependencias.append("monitorías")
    except Exception:
        pass
    # Las sesiones se eliminan automáticamente al borrar el usuario (no bloquean)
    try:
        c.execute("DELETE FROM t_sesion WHERE ses_usu_id_fk = %s", (USU_ID,))
    except Exception:
        pass

    if dependencias:
        c.close()
        raise ValueError(f"No se puede eliminar el usuario {USU_ID} porque tiene {', '.join(dependencias)} asociados. Reasigne o elimine primero esos registros.")
    
    sql = "DELETE FROM t_usuario WHERE usu_id = %s"
    c.execute(sql, (USU_ID,))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Usuario eliminado", "usu_id": USU_ID}


def buscarUsuarios(USU_ID):
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT t_usuario.*, t_rol.rol_nombre
        FROM t_usuario
        LEFT JOIN t_rol ON t_usuario.usu_rol_id_fk = t_rol.rol_id
        WHERE t_usuario.usu_id = %s
    """
    c.execute(sql, (USU_ID,))
    p = c.fetchone()
    c.close()
    
    if p:
        # t_usuario.* = 7 columnas (0-6), t_rol.rol_nombre = índice 7
        u = usuarios(
            usu_id = p[0],
            usu_nombre = p[1],
            usu_rol = p[7] or p[2],  # rol_nombre, fallback a código
            usu_correo = p[3],
            usu_contrasena = p[4],
            usu_estado = p[5],
            usu_ultimo_acceso = p[6]
        ).todic()
        return u
    else:
        return None
