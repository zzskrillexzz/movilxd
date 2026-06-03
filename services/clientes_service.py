from flask import current_app
from models.clientes_model import clientes
from utils.search_builder import SearchBuilder

def listarClientes(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_cliente',
        search_fields=['cli_id', 'cli_nombre', 'cli_apellido', 'cli_correo', 'cli_telefono'],
        exact_fields=['cli_tipo_documento'],
        default_order='cli_id ASC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        cli = clientes(
            cli_id=item['cli_id'],
            cli_tipo_documento=item['cli_tipo_documento'],
            cli_nombre=item['cli_nombre'],
            cli_apellido=item['cli_apellido'],
            cli_telefono=item['cli_telefono'],
            cli_direccion=item['cli_direccion'],
            cli_correo=item['cli_correo']
        ).todic()
        lista.append(cli)

    result['data'] = lista
    return result


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
