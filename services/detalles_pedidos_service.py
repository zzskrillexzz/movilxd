from flask import current_app
from models.detalles_pedidos_model import detalles_pedidos

def listarDetallesPedidos():
    c = current_app.mysql.connection.cursor()
    
    sql = "SELECT det_id, det_cantidad, det_subtotal, det_ped_id_fk, det_pro_id_fk, det_precio_unitario FROM t_detalle_pedido"
    c.execute(sql)
    obj = c.fetchall()
    
    listadetped = []
    
    for x in obj:
        det = detalles_pedidos(
            ID = int(x[0]) if str(x[0]).isdigit() else None,
            CANTIDAD = x[1],
            SUBTOTAL = x[2],
            det_ped_id_fk = x[3],
            det_pro_id_fk = x[4],
            det_precio_unitario = x[5]
        ).diccionario_ped()
        listadetped.append(det)
        
    return listadetped


def registrarDetallesPedidos(ID, CANTIDAD, SUBTOTAL, det_ped_id_fk=None, det_pro_id_fk=None, det_precio_unitario=None):
    c = current_app.mysql.connection.cursor()
    sql = "INSERT INTO t_detalle_pedido (det_id, det_cantidad, det_subtotal, det_ped_id_fk, det_pro_id_fk, det_precio_unitario) VALUES (%s, %s, %s, %s, %s, %s)"
    
    c.execute(sql, (ID, CANTIDAD, SUBTOTAL, det_ped_id_fk, det_pro_id_fk, det_precio_unitario))
    current_app.mysql.connection.commit()
    
    c.close()
    return detalles_pedidos(ID, CANTIDAD, SUBTOTAL, det_ped_id_fk, det_pro_id_fk, det_precio_unitario).diccionario_ped()

def editarDetallesPedidos(ID, CANTIDAD, SUBTOTAL, det_ped_id_fk, det_pro_id_fk, det_precio_unitario):
    c = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_detalle_pedido
        SET det_cantidad=%s, det_subtotal=%s, det_ped_id_fk=%s,
            det_pro_id_fk=%s, det_precio_unitario=%s
        WHERE det_id=%s
    """
    c.execute(sql, (CANTIDAD, SUBTOTAL, det_ped_id_fk, det_pro_id_fk, det_precio_unitario, ID))
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    if filas == 0:
        return None
    return detalles_pedidos(ID, CANTIDAD, SUBTOTAL, det_ped_id_fk, det_pro_id_fk, det_precio_unitario).diccionario_ped()


def eliminarDetallesPedidos(ID):
    c = current_app.mysql.connection.cursor()
    c.execute("DELETE FROM t_detalle_pedido WHERE det_id=%s", (ID,))
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    return filas > 0


def buscarDetallePedido(ID):
    c = current_app.mysql.connection.cursor()
    c.execute("""
        SELECT det_id, det_cantidad, det_subtotal, det_ped_id_fk, det_pro_id_fk, det_precio_unitario
        FROM t_detalle_pedido WHERE det_id=%s
    """, (ID,))
    r = c.fetchone()
    c.close()
    if not r:
        return None
    return detalles_pedidos(r[0], r[1], r[2], r[3], r[4], r[5]).diccionario_ped()