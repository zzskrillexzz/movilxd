from flask import current_app
from models.usuarios_model import usuarios
from utils.search_builder import SearchBuilder
import bcrypt

def listarUsuarios(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_usuario',
        search_fields=['usu_id', 'usu_nombre', 'usu_correo'],
        exact_fields=['usu_rol_id_fk', 'usu_estado'],
        default_order='usu_nombre ASC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        u = usuarios(
            usu_id=item['usu_id'],
            usu_nombre=item['usu_nombre'],
            usu_rol=item.get('usu_rol_id_fk', item.get('usu_rol')),
            usu_correo=item['usu_correo'],
            usu_contrasena=item['usu_contrasena'],
            usu_estado=item['usu_estado'],
            usu_ultimo_acceso=item.get('usu_ultimo_acceso')
        ).todic()
        lista.append(u)

    result['data'] = lista
    return result


def registrarUsuarios(USU_ID, USU_NOMBRE, USU_ROL, USU_CORREO, USU_CONTRASENA, USU_ESTADO, USU_ULTIMO_ACCESO):
    # BUG-003: Hashear contraseña antes de guardar
    contrasena_hash = bcrypt.hashpw(
        USU_CONTRASENA.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    c = current_app.mysql.connection.cursor()
    sql = """
        INSERT INTO t_usuario (usu_id, usu_nombre, usu_rol_id_fk, usu_correo, usu_contrasena, usu_estado, usu_ultimo_acceso) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    c.execute(sql, (USU_ID, USU_NOMBRE, USU_ROL, USU_CORREO, contrasena_hash, USU_ESTADO, USU_ULTIMO_ACCESO))
    current_app.mysql.connection.commit()
    id = c.lastrowid
    c.close()
    return usuarios(USU_ID, USU_NOMBRE, USU_ROL, USU_CORREO, USU_CONTRASENA, USU_ESTADO, USU_ULTIMO_ACCESO).todic()


def editarUsuarios(USU_ID, USU_NOMBRE, USU_ROL, USU_CORREO, USU_CONTRASENA, USU_ESTADO, USU_ULTIMO_ACCESO):
    # BUG-003: Hashear solo si es texto plano (no un hash ya existente)
    if not USU_CONTRASENA.startswith('$2b$') and not USU_CONTRASENA.startswith('$2a$'):
        contrasena_hash = bcrypt.hashpw(
            USU_CONTRASENA.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    else:
        contrasena_hash = USU_CONTRASENA
    c = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_usuario 
        SET usu_nombre=%s, usu_rol_id_fk=%s, usu_correo=%s, usu_contrasena=%s, usu_estado=%s, usu_ultimo_acceso=%s
        WHERE usu_id=%s
    """
    c.execute(sql, (USU_NOMBRE, USU_ROL, USU_CORREO, contrasena_hash, USU_ESTADO, USU_ULTIMO_ACCESO, USU_ID))
    current_app.mysql.connection.commit()
    c.close()
    return usuarios(USU_ID, USU_NOMBRE, USU_ROL, USU_CORREO, USU_CONTRASENA, USU_ESTADO, USU_ULTIMO_ACCESO).todic()


def eliminarUsuarios(USU_ID):
    c = current_app.mysql.connection.cursor()
    sql = "DELETE FROM t_usuario WHERE usu_id = %s"
    c.execute(sql, (USU_ID,))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Usuario eliminado", "usu_id": USU_ID}


def buscarUsuarios(USU_ID):
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT usu_id, usu_nombre, usu_rol_id_fk, usu_correo, usu_contrasena, usu_estado, usu_ultimo_acceso 
        FROM t_usuario 
        WHERE usu_id = %s
    """
    c.execute(sql, (USU_ID,))
    p = c.fetchone()
    c.close()
    
    if p:
        u = usuarios(
            usu_id = p[0],
            usu_nombre = p[1],
            usu_rol = p[2],
            usu_correo = p[3],
            usu_contrasena = p[4],
            usu_estado = p[5],
            usu_ultimo_acceso = p[6]
        ).todic()
        return u
    else:
        return None
