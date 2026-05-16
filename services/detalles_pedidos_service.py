from flask import current_app

def listarDetallesPedidos():
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT det_id, det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal FROM t_detalle_pedido")
    datos = c.fetchall()
    lista = []
    for row in datos:
        lista.append({
            "det_id": row[0],
            "det_ped_id_fk": row[1],
            "det_pro_id_fk": row[2],
            "det_lot_id_fk": row[3],
            "det_cantidad": row[4],
            "det_precio_unitario": float(row[5]) if row[5] else None,
            "det_subtotal": float(row[6]) if row[6] else None
        })
    c.close()
    return lista

def registrarDetallesPedidos(det_id, det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal):
    c = current_app.mysql.connection.cursor()
    sql = """INSERT INTO t_detalle_pedido (det_id, det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal) 
             VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    c.execute(sql, (det_id, det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal))
    current_app.mysql.connection.commit()
    c.close()
    return {"det_id": det_id, "mensaje": "Detalle registrado"}

def editarDetallesPedidos(id, det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal):
    c = current_app.mysql.connection.cursor()
    sql = """UPDATE t_detalle_pedido 
             SET det_ped_id_fk=%s, det_pro_id_fk=%s, det_lot_id_fk=%s, det_cantidad=%s, det_precio_unitario=%s, det_subtotal=%s 
             WHERE det_id=%s"""
    c.execute(sql, (det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal, id))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Detalle actualizado"}

def eliminarDetallesPedidos(id):
    c = current_app.mysql.connection.cursor()
    c.execute("DELETE FROM t_detalle_pedido WHERE det_id=%s", (id,))
    current_app.mysql.connection.commit()
    return c.rowcount > 0

def buscarDetallePedido(id):
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT det_id, det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal FROM t_detalle_pedido WHERE det_id=%s", (id,))
    row = c.fetchone()
    c.close()
    if row:
        return {
            "det_id": row[0],
            "det_ped_id_fk": row[1],
            "det_pro_id_fk": row[2],
            "det_lot_id_fk": row[3],
            "det_cantidad": row[4],
            "det_precio_unitario": float(row[5]) if row[5] else None,
            "det_subtotal": float(row[6]) if row[6] else None
        }
    return None
