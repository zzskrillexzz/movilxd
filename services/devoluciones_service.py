from flask import current_app
from models.devoluciones_model import devoluciones
from utils.search_builder import SearchBuilder
from utils.id_generator import generarIdSiguiente

def listarDevoluciones(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_devolucion',
        search_fields=['dev_id', 'dev_motivo'],
        exact_fields=['dev_fac_id_fk', 'dev_usu_id_fk'],
        range_fields={'dev_fecha': 'date'},
        default_order='dev_fecha DESC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        d = devoluciones(item['dev_id'], item.get('dev_ped_id_fk'), item.get('dev_pro_id_fk'),
                         item.get('dev_lot_id_fk'), item.get('dev_cantidad'),
                         item['dev_motivo'], item.get('dev_fecha'), item.get('dev_usu_id_fk'))
        lista.append(d.todic())

    result['data'] = lista
    return result

def generarId():
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT dev_id FROM t_devolucion ORDER BY dev_id DESC LIMIT 1")
    row = c.fetchone()
    c.close()
    if row:
        last_num = int(row[0].replace('DEV', ''))
        return f"DEV{last_num + 1:03d}"
    return "DEV001"

def eliminarDevolucion(dev_id):
    c = current_app.mysql.connection.cursor()
    c.execute("DELETE FROM t_devolucion WHERE dev_id=%s", (dev_id,))
    current_app.mysql.connection.commit()
    return c.rowcount > 0

def editarDevolucion(dev_id, dev_lot_id_fk, dev_cantidad, dev_motivo, dev_fecha):
    c = current_app.mysql.connection.cursor()
    c.execute("""UPDATE t_devolucion SET dev_lot_id_fk=%s, dev_cantidad=%s, dev_motivo=%s, dev_fecha=%s WHERE dev_id=%s""",
              (dev_lot_id_fk, dev_cantidad, dev_motivo, dev_fecha, dev_id))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Devolucion actualizada"}

def registrarDevolucion(dev_ped_id_fk, dev_pro_id_fk, dev_lot_id_fk, dev_cantidad, dev_motivo, dev_fecha, dev_usu_id_fk):
    dev_id = generarId()
    c = current_app.mysql.connection.cursor()
    
    # BUG-016: Transacción explícita
    try:
        current_app.mysql.connection.begin()

        # ── Insertar la devolución ──
        c.execute("""INSERT INTO t_devolucion (dev_id, dev_ped_id_fk, dev_pro_id_fk, dev_lot_id_fk, dev_cantidad, dev_motivo, dev_fecha, dev_usu_id_fk)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                  (dev_id, dev_ped_id_fk, dev_pro_id_fk, dev_lot_id_fk, dev_cantidad, dev_motivo, dev_fecha, dev_usu_id_fk))

        # ── Reingresar stock al producto (BUG-009: UPDATE atómico) ──
        c.execute(
            "UPDATE t_producto SET pro_cantidad_disponible = pro_cantidad_disponible + %s "
            "WHERE pro_id = %s",
            (dev_cantidad, dev_pro_id_fk)
        )
        c.execute("SELECT pro_cantidad_disponible, pro_precio FROM t_producto WHERE pro_id = %s", (dev_pro_id_fk,))
        row = c.fetchone()
        if row:
            nuevo_stock = row[0] or 0
            precio_unitario = float(row[1]) if row[1] else 0
            stock_anterior = nuevo_stock - dev_cantidad
        else:
            stock_anterior = 0
            precio_unitario = 0
            nuevo_stock = dev_cantidad

        # ── Reingresar stock al lote si aplica ──
        if dev_lot_id_fk:
            c.execute("SELECT lot_cantidad_actual, lot_estado FROM t_lote WHERE lot_id = %s", (dev_lot_id_fk,))
            row_lote = c.fetchone()
            if row_lote:
                stock_lote_anterior = row_lote[0] or 0
                nuevo_stock_lote = stock_lote_anterior + dev_cantidad
                c.execute("UPDATE t_lote SET lot_cantidad_actual = %s WHERE lot_id = %s", (nuevo_stock_lote, dev_lot_id_fk))
                if row_lote[1] == 'Agotado' and nuevo_stock_lote > 0:
                    c.execute("UPDATE t_lote SET lot_estado = 'Activo' WHERE lot_id = %s", (dev_lot_id_fk,))

        # ── Registrar movimiento de inventario (Entrada) ──
        inm_id = generarIdSiguiente('t_inventario_movimiento', 'inm_id', 'INM', 3)
        c.execute("""
            INSERT INTO t_inventario_movimiento (inm_id, inm_tipo_movimiento, inm_pro_id_fk, inm_lot_id_fk, inm_cantidad, inm_fecha, inm_motivo, inm_usu_id_fk)
            VALUES (%s, 'Entrada', %s, %s, %s, %s, %s, %s)
        """, (inm_id, dev_pro_id_fk, dev_lot_id_fk, dev_cantidad, dev_fecha, f"Devolucion {dev_id} - {dev_motivo}", dev_usu_id_fk))

        # ── Registrar monitoria ──
        mon_id = generarIdSiguiente('t_monitoria', 'mon_id', 'MON', 3)
        costo_total = dev_cantidad * precio_unitario
        c.execute("""
            INSERT INTO t_monitoria (mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo,
                                     mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total)
            VALUES (%s, %s, %s, %s, %s, 'Entrada', %s, %s, %s, %s, %s)
        """, (mon_id, dev_pro_id_fk, dev_lot_id_fk, inm_id, dev_fecha, dev_cantidad, stock_anterior, nuevo_stock,
              precio_unitario, costo_total))

        current_app.mysql.connection.commit()
        c.close()
        return {"mensaje": "Devolucion registrada", "id": dev_id}
    except Exception as e:
        current_app.mysql.connection.rollback()
        c.close()
        raise e
