from flask import current_app
from models.detalles_pedidos_model import detalles_pedidos

def listarDetallesPedidos():
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT * FROM t_detalle_pedido")
    datos = c.fetchall()
    lista = []
    for row in datos:
        lista.append({
            "det_id": row[0],
            "det_ped_id_fk": row[1],
            "det_pro_id_fk": row[2],
            "det_cantidad": row[3],
            "det_precio_unitario": row[4],
            "det_subtotal": row[5]
        })
    c.close()
    return lista

def registrarDetallesPedidos(det_id, det_cantidad, det_subtotal, det_ped_id_fk, det_pro_id_fk, det_precio_unitario):
    c = current_app.mysql.connection.cursor()
    sql = """INSERT INTO t_detalle_pedido (det_id, det_ped_id_fk, det_pro_id_fk, det_cantidad, det_precio_unitario, det_subtotal) 
             VALUES (%s, %s, %s, %s, %s, %s)"""
    c.execute(sql, (det_id, det_ped_id_fk, det_pro_id_fk, det_cantidad, det_precio_unitario, det_subtotal))
    current_app.mysql.connection.commit()
    c.close()
    return {
        "det_id": det_id,
        "det_ped_id_fk": det_ped_id_fk,
        "det_pro_id_fk": det_pro_id_fk,
        "det_cantidad": det_cantidad,
        "det_precio_unitario": det_precio_unitario,
        "det_subtotal": det_subtotal
    }

def editarDetallesPedidos(id, det_cantidad, det_subtotal, det_ped_id_fk, det_pro_id_fk, det_precio_unitario):
    c = current_app.mysql.connection.cursor()
    sql = """UPDATE t_detalle_pedido 
             SET det_ped_id_fk=%s, det_pro_id_fk=%s, det_cantidad=%s, det_precio_unitario=%s, det_subtotal=%s 
             WHERE det_id=%s"""
    c.execute(sql, (det_ped_id_fk, det_pro_id_fk, det_cantidad, det_precio_unitario, det_subtotal, id))
    current_app.mysql.connection.commit()
    c.close()
    return {
        "det_id": id,
        "det_ped_id_fk": det_ped_id_fk,
        "det_pro_id_fk": det_pro_id_fk,
        "det_cantidad": det_cantidad,
        "det_precio_unitario": det_precio_unitario,
        "det_subtotal": det_subtotal
    }

def eliminarDetallesPedidos(id):
    c = current_app.mysql.connection.cursor()
    c.execute("DELETE FROM t_detalle_pedido WHERE det_id=%s", (id,))
    current_app.mysql.connection.commit()
    afectadas = c.rowcount
    c.close()
    return afectadas > 0

def buscarDetallePedido(id):
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT * FROM t_detalle_pedido WHERE det_id=%s", (id,))
    row = c.fetchone()
    c.close()
    if row:
        return {
            "det_id": row[0],
            "det_ped_id_fk": row[1],
            "det_pro_id_fk": row[2],
            "det_cantidad": row[3],
            "det_precio_unitario": row[4],
            "det_subtotal": row[5]
        }
    return None