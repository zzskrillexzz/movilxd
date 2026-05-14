from flask import current_app
from models.pedidos_model import pedidos

def listarPedidos():
    c = current_app.mysql.connection.cursor()
    sql = "SELECT ped_id, ped_fecha, ped_metodo_pago, ped_cuenta_bancaria, ped_estado_entrega, ped_total, ped_cli_id_fk, ped_usu_id_fk FROM t_pedido"
    c.execute(sql)
    reg = c.fetchall()
    listav = []
    for p in reg:
        ped = pedidos(
            ID=p[0], FECHA=p[1], METODO_DE_PAGO=p[2], CUENTA_BANCARIA=p[3], ESTADO=p[4],
            TOTAL=p[5], ID_CLIENTE=p[6], ped_usu_id_fk=p[7]
        ).a_diccionario()
        listav.append(ped)
    return listav

def registrarPedidos(ID, FECHA, METODO_DE_PAGO, ESTADO, TOTAL, ID_CLIENTE, ped_cuenta_bancaria=None, ped_usu_id_fk=None):
    c = current_app.mysql.connection.cursor()
    sql = "INSERT INTO t_pedido (ped_id, ped_fecha, ped_metodo_pago, ped_cuenta_bancaria, ped_estado_entrega, ped_total, ped_cli_id_fk, ped_usu_id_fk) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    c.execute(sql, (ID, FECHA, METODO_DE_PAGO, ped_cuenta_bancaria, ESTADO, TOTAL, ID_CLIENTE, ped_usu_id_fk))
    current_app.mysql.connection.commit()
    c.close()
    return pedidos(ID, FECHA, METODO_DE_PAGO, ped_cuenta_bancaria, ESTADO, TOTAL, ID_CLIENTE, ped_usu_id_fk).a_diccionario()

def editarPedidos(ID, FECHA, METODO_DE_PAGO, ESTADO, TOTAL, ID_CLIENTE, ped_cuenta_bancaria=None, ped_usu_id_fk=None):
    c = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_pedido
        SET ped_fecha=%s, ped_metodo_pago=%s, ped_cuenta_bancaria=%s, ped_estado_entrega=%s,
            ped_total=%s, ped_cli_id_fk=%s, ped_usu_id_fk=%s
        WHERE ped_id=%s
    """
    c.execute(sql, (FECHA, METODO_DE_PAGO, ped_cuenta_bancaria, ESTADO, TOTAL, ID_CLIENTE, ped_usu_id_fk, ID))
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    if filas == 0:
        return None
    return pedidos(ID, FECHA, METODO_DE_PAGO, ped_cuenta_bancaria, ESTADO, TOTAL, ID_CLIENTE, ped_usu_id_fk).a_diccionario()


def eliminarPedidos(ID):
    c = current_app.mysql.connection.cursor()
    c.execute("DELETE FROM t_pedido WHERE ped_id=%s", (ID,))
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    return filas > 0


def buscarPedido(ID):
    c = current_app.mysql.connection.cursor()
    c.execute("""
        SELECT ped_id, ped_fecha, ped_metodo_pago, ped_cuenta_bancaria, ped_estado_entrega,
               ped_total, ped_cli_id_fk, ped_usu_id_fk
        FROM t_pedido WHERE ped_id=%s
    """, (ID,))
    r = c.fetchone()
    c.close()
    if not r:
        return None
    return pedidos(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]).a_diccionario()