from flask import current_app
from models.clientes_model import clientes

def listarClientes():
    c = current_app.mysql.connection.cursor()
    
    sql = """
        SELECT cli_id, cli_tipo_documento, cli_nombre, cli_apellido, cli_telefono, cli_direccion, cli_correo 
        FROM t_cliente
    """
    c.execute(sql)
    datos = c.fetchall()
    
    lista = []
    
    for p in datos:
        cli = clientes(
            cli_id = p[0],
            cli_tipo_documento = p[1],
            cli_nombre = p[2],
            cli_apellido = p[3],
            cli_telefono = p[4],
            cli_direccion = p[5],
            cli_correo = p[6]
        ).todic()
        lista.append(cli)
    
    return lista


def registrarClientes(CLI_ID, CLI_TIPO_DOCUMENTO, CLI_NOMBRE, CLI_APELLIDO, CLI_TELEFONO, CLI_DIRECCION, CLI_CORREO):
    c = current_app.mysql.connection.cursor()
    sql = """
        INSERT INTO t_cliente (cli_id, cli_tipo_documento, cli_nombre, cli_apellido, cli_telefono, cli_direccion, cli_correo) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    c.execute(sql, (CLI_ID, CLI_TIPO_DOCUMENTO, CLI_NOMBRE, CLI_APELLIDO, CLI_TELEFONO, CLI_DIRECCION, CLI_CORREO))
    current_app.mysql.connection.commit()
    id = c.lastrowid
    c.close()
    return clientes(CLI_ID, CLI_TIPO_DOCUMENTO, CLI_NOMBRE, CLI_APELLIDO, CLI_TELEFONO, CLI_DIRECCION, CLI_CORREO).todic()


def editarClientes(CLI_ID, CLI_TIPO_DOCUMENTO, CLI_NOMBRE, CLI_APELLIDO, CLI_TELEFONO, CLI_DIRECCION, CLI_CORREO):
    c = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_cliente 
        SET cli_tipo_documento=%s, cli_nombre=%s, cli_apellido=%s, cli_telefono=%s, cli_direccion=%s, cli_correo=%s
        WHERE cli_id=%s
    """
    c.execute(sql, (CLI_TIPO_DOCUMENTO, CLI_NOMBRE, CLI_APELLIDO, CLI_TELEFONO, CLI_DIRECCION, CLI_CORREO, CLI_ID))
    current_app.mysql.connection.commit()
    c.close()
    return clientes(CLI_ID, CLI_TIPO_DOCUMENTO, CLI_NOMBRE, CLI_APELLIDO, CLI_TELEFONO, CLI_DIRECCION, CLI_CORREO).todic()


def eliminarClientes(CLI_ID):
    c = current_app.mysql.connection.cursor()
    sql = "DELETE FROM t_cliente WHERE cli_id = %s"
    c.execute(sql, (CLI_ID,))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Cliente eliminado", "cli_id": CLI_ID}


def buscarClientes(CLI_ID):
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT cli_id, cli_tipo_documento, cli_nombre, cli_apellido, cli_telefono, cli_direccion, cli_correo 
        FROM t_cliente 
        WHERE cli_id = %s
    """
    c.execute(sql, (CLI_ID,))
    p = c.fetchone()
    c.close()
    
    if p:
        return clientes(p[0], p[1], p[2], p[3], p[4], p[5], p[6]).todic()
    return None