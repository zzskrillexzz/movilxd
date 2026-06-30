from datetime import date

from flask import current_app
from models.detalles_compras_model import detalles_compras
from utils.search_builder import SearchBuilder
from utils.id_generator import generarIdSiguiente

# ── Helpers de inventario para compras ──

def _ingresarInventarioDesdeCompra(c, dco_pro_id_fk, dco_lot_id_fk, dco_cantidad,
                                     dco_com_id_fk, dco_precio_compra, dco_subtotal):
    """
    Incrementa stock del lote tras una compra,
    y registra movimiento + monitoria. Recibe cursor abierto.
    """
    c.execute("SELECT COALESCE(SUM(lot_cantidad_actual), 0) FROM t_lote WHERE lot_pro_id_fk = %s",
              (dco_pro_id_fk,))
    stock_total_anterior = c.fetchone()[0] or 0

    # ── 1. Incrementar lote ──
    if dco_lot_id_fk:
        c.execute("SELECT lot_cantidad_actual, lot_estado FROM t_lote WHERE lot_id = %s", (dco_lot_id_fk,))
        row_lote = c.fetchone()
        if row_lote:
            nuevo_stock_lote = (row_lote[0] or 0) + dco_cantidad
            c.execute("UPDATE t_lote SET lot_cantidad_actual = %s WHERE lot_id = %s",
                      (nuevo_stock_lote, dco_lot_id_fk))
            if row_lote[1] == 'Agotado' and nuevo_stock_lote > 0:
                c.execute("UPDATE t_lote SET lot_estado = 'Activo' WHERE lot_id = %s", (dco_lot_id_fk,))

    nuevo_stock_total = stock_total_anterior + dco_cantidad

    # ── 2. Insertar movimiento de inventario (Entrada) ──
    inm_id = generarIdSiguiente('t_inventario_movimiento', 'inm_id', 'INM', 3)
    c.execute("""
        INSERT INTO t_inventario_movimiento
            (inm_id, inm_tipo_movimiento, inm_pro_id_fk, inm_lot_id_fk, inm_cantidad,
             inm_fecha, inm_motivo, inm_usu_id_fk)
        VALUES (%s, 'Entrada', %s, %s, %s, CURDATE(), %s, NULL)
    """, (inm_id, dco_pro_id_fk, dco_lot_id_fk, dco_cantidad, f"Compra {dco_com_id_fk}"))

    # ── 3. Insertar monitoria ──
    mon_id = generarIdSiguiente('t_monitoria', 'mon_id', 'MON', 3)
    c.execute("""
        INSERT INTO t_monitoria
            (mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo,
             mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total)
        VALUES (%s, %s, %s, %s, CURDATE(), 'Entrada', %s, %s, %s, %s, %s)
    """, (mon_id, dco_pro_id_fk, dco_lot_id_fk, inm_id, dco_cantidad,
          stock_total_anterior, nuevo_stock_total, dco_precio_compra, dco_subtotal))


def _revertirIngresoInventario(c, dco_pro_id_fk, dco_lot_id_fk, dco_cantidad,
                                 dco_com_id_fk, dco_precio_compra, dco_subtotal):
    """
    Revierte el ingreso de inventario de una compra:
    descuenta stock del lote, y registra movimiento de Salida + monitoria.
    """
    c.execute("SELECT COALESCE(SUM(lot_cantidad_actual), 0) FROM t_lote WHERE lot_pro_id_fk = %s",
              (dco_pro_id_fk,))
    stock_total_anterior = c.fetchone()[0] or 0

    # ── 1. Descontar lote ──
    if dco_lot_id_fk:
        c.execute("SELECT lot_cantidad_actual FROM t_lote WHERE lot_id = %s", (dco_lot_id_fk,))
        row_lote = c.fetchone()
        if row_lote:
            stock_lote_actual = row_lote[0] or 0
            if stock_lote_actual < dco_cantidad:
                raise ValueError(
                    f"Stock insuficiente en lote {dco_lot_id_fk}: "
                    f"disponible {stock_lote_actual}, solicitado {dco_cantidad}"
                )
            nuevo_stock_lote = stock_lote_actual - dco_cantidad
            c.execute("UPDATE t_lote SET lot_cantidad_actual = %s WHERE lot_id = %s",
                      (nuevo_stock_lote, dco_lot_id_fk))
            if nuevo_stock_lote <= 0:
                c.execute("UPDATE t_lote SET lot_estado = 'Agotado' WHERE lot_id = %s", (dco_lot_id_fk,))

    nuevo_stock_total = stock_total_anterior - dco_cantidad

    # ── 2. Insertar movimiento de inventario (Salida) ──
    inm_id = generarIdSiguiente('t_inventario_movimiento', 'inm_id', 'INM', 3)
    c.execute("""
        INSERT INTO t_inventario_movimiento
            (inm_id, inm_tipo_movimiento, inm_pro_id_fk, inm_lot_id_fk, inm_cantidad,
             inm_fecha, inm_motivo, inm_usu_id_fk)
        VALUES (%s, 'Salida', %s, %s, %s, CURDATE(), %s, NULL)
    """, (inm_id, dco_pro_id_fk, dco_lot_id_fk, dco_cantidad,
          f"Reversion compra {dco_com_id_fk}"))

    # ── 3. Insertar monitoria ──
    mon_id = generarIdSiguiente('t_monitoria', 'mon_id', 'MON', 3)
    c.execute("""
        INSERT INTO t_monitoria
            (mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo,
             mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total)
        VALUES (%s, %s, %s, %s, CURDATE(), 'Salida', %s, %s, %s, %s, %s)
    """, (mon_id, dco_pro_id_fk, dco_lot_id_fk, inm_id, dco_cantidad,
          stock_total_anterior, nuevo_stock_total, dco_precio_compra, dco_subtotal))


# ── CRUD principal ──

def listarDetallesCompras(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_detalle_compra',
        search_fields=['dco_id', 'dco_com_id_fk', 'dco_pro_id_fk'],
        exact_fields=['dco_com_id_fk', 'dco_pro_id_fk', 'dco_lot_id_fk'],
        default_order='dco_id DESC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        dc = detalles_compras(item['dco_id'], item['dco_com_id_fk'], item['dco_pro_id_fk'],
                              item.get('dco_lot_id_fk'), item['dco_cantidad'],
                              item['dco_precio_compra'], item['dco_subtotal']).todic()
        lista.append(dc)

    result['data'] = lista
    return result


def _generarLotNumero(c, pro_id, fecha_vencimiento):
    c.execute("SELECT pro_nombre FROM t_producto WHERE pro_id = %s", (pro_id,))
    row = c.fetchone()
    abrev = row[0][:3].upper() if row and row[0] else 'XXX'
    if isinstance(fecha_vencimiento, str) and len(fecha_vencimiento) >= 4:
        anio = fecha_vencimiento[:4]
    else:
        anio = str(fecha_vencimiento.year) if hasattr(fecha_vencimiento, 'year') else str(date.today().year)
    clave = f"{abrev}-{anio}"
    c.execute("""
        SELECT COUNT(*) FROM t_lote WHERE lot_numero LIKE %s
    """, (f"LT-{clave}-%",))
    seq = str(c.fetchone()[0] + 1).zfill(3)
    return f"LT-{clave}-{seq}"


def registrarDetallesCompras(DCO_ID, DCO_COM_ID_FK, DCO_PRO_ID_FK, DCO_LOT_ID_FK,
                              DCO_CANTIDAD, DCO_PRECIO_COMPRA, DCO_SUBTOTAL,
                              DCO_FECHA_FABRICACION=None, DCO_FECHA_VENCIMIENTO=None,
                              DCO_PROV_ID_FK=None):
    c = current_app.mysql.connection.cursor()
    try:
        current_app.mysql.connection.begin()

        pendiente = False

        # Auto-crear lote si no se proporcionó uno y hay fechas
        if not DCO_LOT_ID_FK and DCO_FECHA_FABRICACION and DCO_FECHA_VENCIMIENTO and DCO_PROV_ID_FK:
            lot_id = generarIdSiguiente('t_lote', 'lot_id', 'LOT', 3)
            lot_numero = _generarLotNumero(c, DCO_PRO_ID_FK, DCO_FECHA_VENCIMIENTO)
            c.execute("""
                INSERT INTO t_lote
                    (lot_id, lot_numero, lot_fecha_fabricacion, lot_fecha_vencimiento,
                     lot_cantidad_inicial, lot_cantidad_actual, lot_pro_id_fk, lot_prov_id_fk, lot_estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (lot_id, lot_numero, DCO_FECHA_FABRICACION, DCO_FECHA_VENCIMIENTO,
                  DCO_CANTIDAD, 0, DCO_PRO_ID_FK, DCO_PROV_ID_FK, 'Pendiente'))
            DCO_LOT_ID_FK = lot_id
            pendiente = True

        # Ingresar al inventario solo si el lote no es Pendiente
        if DCO_LOT_ID_FK and not pendiente:
            _ingresarInventarioDesdeCompra(
                c, DCO_PRO_ID_FK, DCO_LOT_ID_FK, DCO_CANTIDAD,
                DCO_COM_ID_FK, DCO_PRECIO_COMPRA, DCO_SUBTOTAL
            )
        elif DCO_LOT_ID_FK and pendiente:
            # Para lotes Pendiente, actualizar cantidad_inicial si el lote ya existia
            # (no deberia pasar en flujo normal, pero por seguridad)
            pass

        # Insertar el detalle de compra
        sql = """
            INSERT INTO t_detalle_compra
                (dco_id, dco_com_id_fk, dco_pro_id_fk, dco_lot_id_fk,
                 dco_cantidad, dco_precio_compra, dco_subtotal)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        c.execute(sql, (DCO_ID, DCO_COM_ID_FK, DCO_PRO_ID_FK, DCO_LOT_ID_FK,
                        DCO_CANTIDAD, DCO_PRECIO_COMPRA, DCO_SUBTOTAL))

        current_app.mysql.connection.commit()
        c.close()
        return detalles_compras(DCO_ID, DCO_COM_ID_FK, DCO_PRO_ID_FK, DCO_LOT_ID_FK,
                                DCO_CANTIDAD, DCO_PRECIO_COMPRA, DCO_SUBTOTAL).todic()
    except Exception as e:
        current_app.mysql.connection.rollback()
        c.close()
        raise e


def editarDetallesCompras(DCO_ID, data):
    c = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_detalle_compra
        SET dco_com_id_fk=%s, dco_pro_id_fk=%s, dco_lot_id_fk=%s,
            dco_cantidad=%s, dco_precio_compra=%s, dco_subtotal=%s
        WHERE dco_id=%s
    """
    c.execute(sql, (
        data.get('dco_com_id_fk'), data.get('dco_pro_id_fk'), data.get('dco_lot_id_fk'),
        data.get('dco_cantidad'), data.get('dco_precio_compra'), data.get('dco_subtotal'),
        DCO_ID
    ))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Detalle de compra actualizado"}


def eliminarDetallesCompras(DCO_ID):
    c = current_app.mysql.connection.cursor()
    try:
        current_app.mysql.connection.begin()

        # Obtener datos del detalle antes de eliminarlo para revertir inventario
        c.execute("""
            SELECT dco_com_id_fk, dco_pro_id_fk, dco_lot_id_fk,
                   dco_cantidad, dco_precio_compra, dco_subtotal
            FROM t_detalle_compra WHERE dco_id = %s
        """, (DCO_ID,))
        detalle = c.fetchone()

        c.execute("DELETE FROM t_detalle_compra WHERE dco_id = %s", (DCO_ID,))

        # Revertir inventario si el detalle existía
        if detalle:
            dco_com_id_fk, dco_pro_id_fk, dco_lot_id_fk, dco_cantidad, \
                dco_precio_compra, dco_subtotal = detalle
            _revertirIngresoInventario(
                c, dco_pro_id_fk, dco_lot_id_fk, dco_cantidad,
                dco_com_id_fk, dco_precio_compra, dco_subtotal
            )

        current_app.mysql.connection.commit()
        return c.rowcount > 0
    except Exception as e:
        current_app.mysql.connection.rollback()
        c.close()
        raise e


def buscarDetallesCompras(DCO_ID):
    c = current_app.mysql.connection.cursor()
    c.execute("""
        SELECT dco_id, dco_com_id_fk, dco_pro_id_fk, dco_lot_id_fk,
               dco_cantidad, dco_precio_compra, dco_subtotal
        FROM t_detalle_compra WHERE dco_id = %s
    """, (DCO_ID,))
    row = c.fetchone()
    c.close()
    if row:
        return {
            "dco_id": row[0],
            "dco_com_id_fk": row[1],
            "dco_pro_id_fk": row[2],
            "dco_lot_id_fk": row[3],
            "dco_cantidad": row[4],
            "dco_precio_compra": float(row[5]) if row[5] else None,
            "dco_subtotal": float(row[6]) if row[6] else None
        }
    return None
