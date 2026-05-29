from flask import current_app
from models.lotes_model import lotes
from utils.search_builder import SearchBuilder

def listarLotes(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_lote',
        search_fields=['lot_id', 'lot_numero', 'lot_estado'],
        exact_fields=['lot_estado', 'lot_pro_id_fk', 'lot_prov_id_fk'],
        range_fields={'lot_fecha_fabricacion': 'date', 'lot_fecha_vencimiento': 'date', 'lot_cantidad_actual': 'int'},
        default_order='lot_id ASC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        l = lotes(
            lot_id=item['lot_id'],
            lot_numero=item['lot_numero'],
            lot_fecha_fabricacion=item['lot_fecha_fabricacion'],
            lot_fecha_vencimiento=item['lot_fecha_vencimiento'],
            lot_cantidad_inicial=item['lot_cantidad_inicial'],
            lot_cantidad_actual=item['lot_cantidad_actual'],
            lot_pro_id_fk=item['lot_pro_id_fk'],
            lot_prov_id_fk=item['lot_prov_id_fk'],
            lot_estado=item['lot_estado']
        ).todic()
        lista.append(l)

    result['data'] = lista
    return result

def registrarLotes(LOT_ID, LOT_NUMERO, LOT_FECHA_FABRICACION, LOT_FECHA_VENCIMIENTO, 
                   LOT_CANTIDAD_INICIAL, LOT_CANTIDAD_ACTUAL, LOT_PRO_ID_FK, LOT_PROV_ID_FK, LOT_ESTADO):
    c = current_app.mysql.connection.cursor()
    sql = """
        INSERT INTO t_lote (lot_id, lot_numero, lot_fecha_fabricacion, lot_fecha_vencimiento, 
                            lot_cantidad_inicial, lot_cantidad_actual, lot_pro_id_fk, lot_prov_id_fk, lot_estado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    c.execute(sql, (LOT_ID, LOT_NUMERO, LOT_FECHA_FABRICACION, LOT_FECHA_VENCIMIENTO, 
                    LOT_CANTIDAD_INICIAL, LOT_CANTIDAD_ACTUAL, LOT_PRO_ID_FK, LOT_PROV_ID_FK, LOT_ESTADO))
    current_app.mysql.connection.commit()
    c.close()
    return lotes(LOT_ID, LOT_NUMERO, LOT_FECHA_FABRICACION, LOT_FECHA_VENCIMIENTO, 
                 LOT_CANTIDAD_INICIAL, LOT_CANTIDAD_ACTUAL, LOT_PRO_ID_FK, LOT_PROV_ID_FK, LOT_ESTADO).todic()

def buscarLotes(LOT_ID):
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT lot_id, lot_numero, lot_fecha_fabricacion, lot_fecha_vencimiento, 
               lot_cantidad_inicial, lot_cantidad_actual, lot_pro_id_fk, lot_prov_id_fk, lot_estado 
        FROM t_lote WHERE lot_id = %s
    """
    c.execute(sql, (LOT_ID,))
    dato = c.fetchone()
    if dato:
        return lotes(dato[0], dato[1], dato[2], dato[3], dato[4], dato[5], dato[6], dato[7], dato[8]).todic()
    return None

def editarLotes(LOT_ID, data):
    c = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_lote 
        SET lot_numero = %s, lot_fecha_fabricacion = %s, lot_fecha_vencimiento = %s, 
            lot_cantidad_inicial = %s, lot_cantidad_actual = %s, lot_pro_id_fk = %s, 
            lot_prov_id_fk = %s, lot_estado = %s 
        WHERE lot_id = %s
    """
    c.execute(sql, (
        data.get('lot_numero'), data.get('lot_fecha_fabricacion'), data.get('lot_fecha_vencimiento'),
        data.get('lot_cantidad_inicial'), data.get('lot_cantidad_actual'), data.get('lot_pro_id_fk'),
        data.get('lot_prov_id_fk'), data.get('lot_estado'), LOT_ID
    ))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Lote actualizado correctamente"}

def eliminarLotes(LOT_ID, fuerza=False):
    """
    Elimina un lote.
    Si fuerza=True, elimina en cascada todos los registros que dependan de él.
    Si fuerza=False (default), solo elimina si no tiene dependencias.
    """
    c = current_app.mysql.connection.cursor()

    # Verificar que exista
    c.execute("SELECT lot_id FROM t_lote WHERE lot_id = %s", (LOT_ID,))
    if not c.fetchone():
        c.close()
        return {"ok": False, "mensaje": f"No existe un lote con ID {LOT_ID}"}, 404

    if fuerza:
        # Eliminar en cascada
        # 1. Alertas de vencimiento
        c.execute("DELETE FROM t_alerta_vencimiento WHERE alv_lot_id_fk = %s", (LOT_ID,))
        # 2. Detalles de compra
        c.execute("DELETE FROM t_detalle_compra WHERE dco_lot_id_fk = %s", (LOT_ID,))
        # 3. Movimientos de inventario + su monitoria
        c.execute("SELECT inm_id FROM t_inventario_movimiento WHERE inm_lot_id_fk = %s", (LOT_ID,))
        for (inm_id,) in c.fetchall():
            c.execute("DELETE FROM t_monitoria WHERE mon_inm_id_fk = %s", (inm_id,))
        c.execute("DELETE FROM t_inventario_movimiento WHERE inm_lot_id_fk = %s", (LOT_ID,))
        # 4. Monitoría directa
        c.execute("DELETE FROM t_monitoria WHERE mon_lot_id_fk = %s", (LOT_ID,))
        # 5. Detalles de pedido
        c.execute("DELETE FROM t_detalle_pedido WHERE det_lot_id_fk = %s", (LOT_ID,))
        # 6. El lote mismo
        c.execute("DELETE FROM t_lote WHERE lot_id = %s", (LOT_ID,))
        current_app.mysql.connection.commit()
        c.close()
        return {"ok": True, "mensaje": f"Lote {LOT_ID} eliminado junto con todos sus registros dependientes"}, 200
    else:
        # Verificar dependencias
        deps = []
        c.execute("SELECT COUNT(*) FROM t_alerta_vencimiento WHERE alv_lot_id_fk = %s", (LOT_ID,))
        if c.fetchone()[0] > 0: deps.append("alertas de vencimiento")
        c.execute("SELECT COUNT(*) FROM t_detalle_compra WHERE dco_lot_id_fk = %s", (LOT_ID,))
        if c.fetchone()[0] > 0: deps.append("detalles de compra")
        c.execute("SELECT COUNT(*) FROM t_inventario_movimiento WHERE inm_lot_id_fk = %s", (LOT_ID,))
        if c.fetchone()[0] > 0: deps.append("movimientos de inventario")
        c.execute("SELECT COUNT(*) FROM t_monitoria WHERE mon_lot_id_fk = %s", (LOT_ID,))
        if c.fetchone()[0] > 0: deps.append("registros de monitoría")
        c.execute("SELECT COUNT(*) FROM t_detalle_pedido WHERE det_lot_id_fk = %s", (LOT_ID,))
        if c.fetchone()[0] > 0: deps.append("detalles de pedido")
        if deps:
            c.close()
            return {
                "ok": False,
                "mensaje": f"No se puede eliminar el lote {LOT_ID} porque tiene registros dependientes en: {', '.join(deps)}. Usa fuerza=true para eliminar en cascada."
            }, 409
        c.execute("DELETE FROM t_lote WHERE lot_id = %s", (LOT_ID,))
        current_app.mysql.connection.commit()
        c.close()
        return {"ok": True, "mensaje": f"Lote {LOT_ID} eliminado correctamente"}, 200
