from flask import current_app
from utils.search_builder import SearchBuilder
from utils.id_generator import generarIdSiguiente

def listarDetallesPedidos(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_detalle_pedido',
        search_fields=['det_id', 'det_ped_id_fk', 'det_pro_id_fk'],
        exact_fields=['det_ped_id_fk', 'det_pro_id_fk', 'det_lot_id_fk'],
        default_order='det_id ASC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        lista.append({
            "det_id": item['det_id'],
            "det_ped_id_fk": item['det_ped_id_fk'],
            "det_pro_id_fk": item['det_pro_id_fk'],
            "det_lot_id_fk": item.get('det_lot_id_fk'),
            "det_cantidad": item['det_cantidad'],
            "det_precio_unitario": float(item['det_precio_unitario']) if item.get('det_precio_unitario') else None,
            "det_subtotal": float(item['det_subtotal']) if item.get('det_subtotal') else None
        })

    result['data'] = lista
    return result

def _descontarInventario(c, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_ped_id_fk, det_precio_unitario, det_subtotal):
    """
    Descuenta stock del producto y lote, y registra movimiento + monitoria.
    Recibe un cursor abierto y hace commit internamente.
    
    BUG-009: Usa UPDATE atómico para evitar TOCTOU.
    """
    # ── 1. Validar y descontar producto (atómicamente) ──
    c.execute(
        "UPDATE t_producto SET pro_cantidad_disponible = pro_cantidad_disponible - %s "
        "WHERE pro_id = %s AND pro_cantidad_disponible >= %s",
        (det_cantidad, det_pro_id_fk, det_cantidad)
    )
    if c.rowcount == 0:
        # Verificar si el producto existe o si fue por stock insuficiente
        c.execute("SELECT pro_cantidad_disponible FROM t_producto WHERE pro_id = %s", (det_pro_id_fk,))
        row = c.fetchone()
        if not row:
            raise ValueError(f"Producto {det_pro_id_fk} no encontrado")
        raise ValueError(f"Stock insuficiente para {det_pro_id_fk}: disponible {row[0] or 0}, solicitado {det_cantidad}")
    
    # Obtener stock anterior para monitoria
    c.execute("SELECT pro_cantidad_disponible FROM t_producto WHERE pro_id = %s", (det_pro_id_fk,))
    nuevo_stock = c.fetchone()[0] or 0
    stock_anterior = nuevo_stock + det_cantidad

    # ── 2. Descontar lote(s) ──
    # Si no se especifica lote, auto-asignar el más antiguo con stock disponible (FIFO)
    lotes_a_descontar = []
    if det_lot_id_fk:
        # Lote específico
        c.execute("SELECT lot_id, lot_cantidad_actual FROM t_lote WHERE lot_id = %s", (det_lot_id_fk,))
        row_lote = c.fetchone()
        if row_lote:
            lotes_a_descontar = [(row_lote[0], row_lote[1] or 0)]
    else:
        # Auto-asignar lotes disponibles para este producto (FIFO por fecha de vencimiento)
        c.execute("""
            SELECT lot_id, lot_cantidad_actual FROM t_lote
            WHERE lot_pro_id_fk = %s AND lot_estado = 'Activo' AND lot_cantidad_actual > 0
            ORDER BY lot_fecha_vencimiento ASC, lot_fecha_fabricacion ASC
        """, (det_pro_id_fk,))
        lotes_a_descontar = [(r[0], r[1] or 0) for r in c.fetchall()]

    cantidad_restante = det_cantidad
    lotes_usados = []
    for lot_id, stock_lote in lotes_a_descontar:
        if cantidad_restante <= 0:
            break
        a_descontar = min(cantidad_restante, stock_lote)
        nuevo_stock_lote = stock_lote - a_descontar
        c.execute("UPDATE t_lote SET lot_cantidad_actual = %s WHERE lot_id = %s", (nuevo_stock_lote, lot_id))
        if nuevo_stock_lote <= 0:
            c.execute("UPDATE t_lote SET lot_estado = 'Agotado' WHERE lot_id = %s", (lot_id,))
        cantidad_restante -= a_descontar
        lotes_usados.append(lot_id)
    # Actualizar det_lot_id_fk con el primer lote usado (para el movimiento)
    if lotes_usados:
        det_lot_id_fk = lotes_usados[0]

    # ── 3. Insertar movimiento de inventario ──
    inm_id = generarIdSiguiente('t_inventario_movimiento', 'inm_id', 'INM', 3)
    c.execute("""
        INSERT INTO t_inventario_movimiento (inm_id, inm_tipo_movimiento, inm_pro_id_fk, inm_lot_id_fk, inm_cantidad, inm_fecha, inm_motivo, inm_usu_id_fk)
        VALUES (%s, 'Salida', %s, %s, %s, CURDATE(), %s, NULL)
    """, (inm_id, det_pro_id_fk, det_lot_id_fk, det_cantidad, f"Venta {det_ped_id_fk}"))

    # ── 4. Insertar monitoria ──
    mon_id = generarIdSiguiente('t_monitoria', 'mon_id', 'MON', 3)
    c.execute("""
        INSERT INTO t_monitoria (mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo,
                                 mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total)
        VALUES (%s, %s, %s, %s, CURDATE(), 'Salida', %s, %s, %s, %s, %s)
    """, (mon_id, det_pro_id_fk, det_lot_id_fk, inm_id, det_cantidad, stock_anterior, nuevo_stock,
          det_precio_unitario, det_subtotal))

    return det_lot_id_fk


def _reingresarInventario(c, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_ped_id_fk, det_precio_unitario, det_subtotal):
    """
    Revierte el descuento: suma stock al producto y lote, y registra movimiento + monitoria de Entrada.
    Recibe un cursor abierto y hace commit internamente.
    
    BUG-009: Usa UPDATE atómico.
    """
    # ── 1. Reingresar producto (atómico) ──
    c.execute(
        "UPDATE t_producto SET pro_cantidad_disponible = pro_cantidad_disponible + %s "
        "WHERE pro_id = %s",
        (det_cantidad, det_pro_id_fk)
    )
    if c.rowcount == 0:
        raise ValueError(f"Producto {det_pro_id_fk} no encontrado")
    
    # Obtener nuevo stock para monitoria
    c.execute("SELECT pro_cantidad_disponible FROM t_producto WHERE pro_id = %s", (det_pro_id_fk,))
    nuevo_stock = c.fetchone()[0] or 0
    stock_anterior = nuevo_stock - det_cantidad

    # ── 2. Reingresar lote si aplica ──
    stock_lote_anterior = None
    if det_lot_id_fk:
        c.execute("SELECT lot_cantidad_actual, lot_estado FROM t_lote WHERE lot_id = %s", (det_lot_id_fk,))
        row_lote = c.fetchone()
        if row_lote:
            stock_lote_anterior = row_lote[0] or 0
            nuevo_stock_lote = stock_lote_anterior + det_cantidad
            c.execute("UPDATE t_lote SET lot_cantidad_actual = %s WHERE lot_id = %s", (nuevo_stock_lote, det_lot_id_fk))
            # Reactivar lote si estaba agotado
            if row_lote[1] == 'Agotado' and nuevo_stock_lote > 0:
                c.execute("UPDATE t_lote SET lot_estado = 'Activo' WHERE lot_id = %s", (det_lot_id_fk,))

    # ── 3. Insertar movimiento de inventario ──
    inm_id = generarIdSiguiente('t_inventario_movimiento', 'inm_id', 'INM', 3)
    c.execute("""
        INSERT INTO t_inventario_movimiento (inm_id, inm_tipo_movimiento, inm_pro_id_fk, inm_lot_id_fk, inm_cantidad, inm_fecha, inm_motivo, inm_usu_id_fk)
        VALUES (%s, 'Entrada', %s, %s, %s, CURDATE(), %s, NULL)
    """, (inm_id, det_pro_id_fk, det_lot_id_fk, det_cantidad, f"Reversion venta {det_ped_id_fk}"))

    # ── 4. Insertar monitoria ──
    mon_id = generarIdSiguiente('t_monitoria', 'mon_id', 'MON', 3)
    c.execute("""
        INSERT INTO t_monitoria (mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo,
                                 mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total)
        VALUES (%s, %s, %s, %s, CURDATE(), 'Entrada', %s, %s, %s, %s, %s)
    """, (mon_id, det_pro_id_fk, det_lot_id_fk, inm_id, det_cantidad, stock_anterior, nuevo_stock,
          det_precio_unitario, det_subtotal))


def registrarDetallesPedidos(det_id, det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal):
    c = current_app.mysql.connection.cursor()
    
    # BUG-016: Transacción explícita
    try:
        current_app.mysql.connection.begin()
        
        # BUG-015: Validar stock ANTES de hacer el INSERT
        # _descontarInventario valida stock internamente (UPDATE atómico rowcount=0 → error)
        lot_id_real = _descontarInventario(c, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_ped_id_fk, det_precio_unitario, det_subtotal)
        
        # Solo si el stock es suficiente, insertar el detalle
        sql = """INSERT INTO t_detalle_pedido (det_id, det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        c.execute(sql, (det_id, det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal))

        # Si se auto-asignó un lote, actualizar el detalle para trazabilidad
        if lot_id_real and lot_id_real != det_lot_id_fk:
            c.execute("UPDATE t_detalle_pedido SET det_lot_id_fk = %s WHERE det_id = %s", (lot_id_real, det_id))

        current_app.mysql.connection.commit()
        c.close()
        return {"det_id": det_id, "mensaje": "Detalle registrado"}
    except Exception as e:
        current_app.mysql.connection.rollback()
        c.close()
        raise e

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
    
    # BUG-016: Transacción explícita
    try:
        current_app.mysql.connection.begin()

        # Obtener datos del detalle antes de eliminarlo para revertir inventario
        c.execute("SELECT det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal FROM t_detalle_pedido WHERE det_id=%s", (id,))
        detalle = c.fetchone()

        c.execute("DELETE FROM t_detalle_pedido WHERE det_id=%s", (id,))

        # Revertir inventario si el detalle existía
        if detalle:
            det_ped_id_fk, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal = detalle
            _reingresarInventario(c, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_ped_id_fk, det_precio_unitario, det_subtotal)

        current_app.mysql.connection.commit()
        return c.rowcount > 0
    except Exception as e:
        current_app.mysql.connection.rollback()
        c.close()
        raise e

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
