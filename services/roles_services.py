from flask import current_app
from models.roles_model import roles

def listarRoles():
    c = current_app.mysql.connection.cursor()
    sql = "SELECT rol_id, rol_nombre, rol_descripcion, rol_estado FROM t_rol"
    c.execute(sql)
    reg = c.fetchall()
    lista = []
    for p in reg:
        rol = roles(
            rol_id=p[0],
            rol_nombre=p[1],
            rol_descripcion=p[2],
            rol_estado=p[3]
        ).toDic()
        lista.append(rol)
    return lista

def registrarRoles(data):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            INSERT INTO t_rol (rol_id, rol_nombre, rol_descripcion, rol_estado)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data.get('id'),
            data.get('nombre'),
            data.get('descripcion'),
            data.get('estado', 1)
        ))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Rol registrado correctamente"}
    except Exception as e:
        raise e

def editarRoles(data):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            UPDATE t_rol 
            SET rol_nombre = %s, rol_descripcion = %s, rol_estado = %s
            WHERE rol_id = %s
        """
        cursor.execute(sql, (
            data.get('nombre'),
            data.get('descripcion'),
            data.get('estado', 1),
            data.get('id')
        ))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Rol actualizado correctamente"}
    except Exception as e:
        raise e

def eliminarRoles(rol_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # Verificar si hay usuarios con este rol
        cursor.execute("SELECT usu_id FROM t_usuario WHERE usu_rol_id_fk = %s LIMIT 1", (rol_id,))
        if cursor.fetchone():
            cursor.close()
            return {"mensaje": "No se puede eliminar: hay usuarios con este rol", "error": True}
        
        sql = "DELETE FROM t_rol WHERE rol_id = %s"
        cursor.execute(sql, (rol_id,))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Rol eliminado correctamente"}
    except Exception as e:
        raise e

def buscarRoles(rol_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = "SELECT rol_id, rol_nombre, rol_descripcion, rol_estado FROM t_rol WHERE rol_id = %s"
        cursor.execute(sql, (rol_id,))
        p = cursor.fetchone()
        cursor.close()
        
        if p:
            return roles(
                rol_id=p[0],
                rol_nombre=p[1],
                rol_descripcion=p[2],
                rol_estado=p[3]
            ).toDic()
        return None
    except Exception as e:
        raise e