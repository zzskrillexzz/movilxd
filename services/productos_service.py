from flask import current_app
from models.productos_model import productos
from utils.search_builder import SearchBuilder

def listarProductos(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_producto',
        search_fields=['pro_id', 'pro_nombre', 'pro_categoria', 'pro_descripcion'],
        exact_fields=['pro_estado', 'pro_categoria', 'pro_prov_id_fk', 'pro_control_especial'],
        range_fields={'pro_precio': 'decimal', 'pro_cantidad_disponible': 'int', 'pro_stock_minimo': 'int'},
        join_clause='LEFT JOIN t_proveedor ON pro_prov_id_fk = prov_id',
        select_columns='t_producto.*, prov_nombre as proveedor_nombre',
        default_order='pro_id ASC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        prod = productos(
            proID=item['pro_id'], proNombre=item['pro_nombre'], proCategoria=item['pro_categoria'],
            proDescripcion=item['pro_descripcion'], proPrecio=item['pro_precio'],
            proCantidad=item['pro_cantidad_disponible'], proStockMinimo=item['pro_stock_minimo'],
            proFechaCaducidad=item['pro_fecha_caducidad'],
            proRegistroInvima=item['pro_registro_invima'],
            proFechaVencimientoRegistro=item['pro_fecha_vencimiento_registro'],
            proControlEspecial=item['pro_control_especial'], proTipoControl=item['pro_tipo_control'],
            proEstado=item['pro_estado'], proIDprovedor=item['pro_prov_id_fk']
        ).toDic()
        lista.append(prod)

    result['data'] = lista
    return result

def registrarProductos(data):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            INSERT INTO t_producto (pro_id, pro_nombre, pro_categoria, pro_descripcion, pro_precio,
                                    pro_cantidad_disponible, pro_stock_minimo, pro_fecha_caducidad,
                                    pro_registro_invima, pro_fecha_vencimiento_registro,
                                    pro_control_especial, pro_tipo_control, pro_estado, pro_prov_id_fk)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data.get('id'), data.get('nombre'), data.get('categoria'), data.get('descripcion'),
            data.get('precio'), data.get('cantidad_disponible'), data.get('stock_minimo', 10),
            data.get('fecha_caducidad'), data.get('registro_invima'),
            data.get('fecha_vencimiento_registro'),
            1 if data.get('control_especial') else 0,
            data.get('tipo_control'), data.get('estado', 'Activo'), data.get('proveedor_id')
        ))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Producto registrado correctamente"}
    except Exception as e:
        raise e

def _forzar_eliminar_lote(cursor, lot_id):
    """
    Elimina un lote y todos sus registros dependientes en cascada.
    Recibe un cursor abierto (sin commit).
    """
    # 1. Alertas de vencimiento que referencian al lote
    cursor.execute("DELETE FROM t_alerta_vencimiento WHERE alv_lot_id_fk = %s", (lot_id,))
    # 2. Detalles de compra que referencian al lote
    cursor.execute("DELETE FROM t_detalle_compra WHERE dco_lot_id_fk = %s", (lot_id,))
    # 3. Movimientos de inventario + su monitoria
    cursor.execute("SELECT inm_id FROM t_inventario_movimiento WHERE inm_lot_id_fk = %s", (lot_id,))
    for (inm_id,) in cursor.fetchall():
        cursor.execute("DELETE FROM t_monitoria WHERE mon_inm_id_fk = %s", (inm_id,))
    cursor.execute("DELETE FROM t_inventario_movimiento WHERE inm_lot_id_fk = %s", (lot_id,))
    # 4. Monitoría que referencia al lote directamente
    cursor.execute("DELETE FROM t_monitoria WHERE mon_lot_id_fk = %s", (lot_id,))
    # 5. Detalles de pedido que referencian al lote (sin FK explicito pero existe la columna)
    cursor.execute("DELETE FROM t_detalle_pedido WHERE det_lot_id_fk = %s", (lot_id,))
    # 6. El lote mismo
    cursor.execute("DELETE FROM t_lote WHERE lot_id = %s", (lot_id,))


def eliminarProductos(pro_id, fuerza=False):
    """
    Elimina un producto.
    Si fuerza=True, elimina en cascada todo lo que dependa de él (lotes, movimientos, etc.).
    Si fuerza=False (default), solo elimina si no tiene dependencias.
    """
    try:
        cursor = current_app.mysql.connection.cursor()

        # Verificar que exista
        cursor.execute("SELECT pro_nombre FROM t_producto WHERE pro_id = %s", (pro_id,))
        prod = cursor.fetchone()
        if not prod:
            cursor.close()
            return {"ok": False, "mensaje": f"No existe un producto con ID {pro_id}"}, 404

        if fuerza:
            # ── Eliminación forzada en cascada ──
            # 1. Lotes del producto (con sus dependencias)
            cursor.execute("SELECT lot_id FROM t_lote WHERE lot_pro_id_fk = %s", (pro_id,))
            lots = [r[0] for r in cursor.fetchall()]
            for lot_id in lots:
                _forzar_eliminar_lote(cursor, lot_id)

            # 2. Detalles de pedido que referencian al producto
            cursor.execute("DELETE FROM t_detalle_pedido WHERE det_pro_id_fk = %s", (pro_id,))

            # 3. Detalles de compra
            cursor.execute("DELETE FROM t_detalle_compra WHERE dco_pro_id_fk = %s", (pro_id,))

            # 4. Movimientos de inventario (los que no se fueron por lote)
            cursor.execute("SELECT inm_id FROM t_inventario_movimiento WHERE inm_pro_id_fk = %s", (pro_id,))
            for (inm_id,) in cursor.fetchall():
                cursor.execute("DELETE FROM t_monitoria WHERE mon_inm_id_fk = %s", (inm_id,))
            cursor.execute("DELETE FROM t_inventario_movimiento WHERE inm_pro_id_fk = %s", (pro_id,))

            # 5. Monitoría restante
            cursor.execute("DELETE FROM t_monitoria WHERE mon_pro_id_fk = %s", (pro_id,))

            # 6. Alertas de vencimiento
            cursor.execute("DELETE FROM t_alerta_vencimiento WHERE alv_pro_id_fk = %s", (pro_id,))

            # 7. Relaciones proveedor-producto
            cursor.execute("DELETE FROM t_proveedor_producto WHERE ppp_pro_id_fk = %s", (pro_id,))

            # 8. El producto mismo
            cursor.execute("DELETE FROM t_producto WHERE pro_id = %s", (pro_id,))
            current_app.mysql.connection.commit()
            filas = cursor.rowcount
            cursor.close()

            if filas == 0:
                return {"ok": False, "mensaje": "No se pudo eliminar el producto"}, 500

            return {"ok": True, "mensaje": f"Producto {pro_id} eliminado junto con {len(lots)} lote(s) y todos sus registros dependientes"}, 200

        else:
            # ── Eliminación segura (sin dependencias) ──
            dependencias = []

            cursor.execute("SELECT COUNT(*) FROM t_lote WHERE lot_pro_id_fk = %s", (pro_id,))
            if cursor.fetchone()[0] > 0:
                dependencias.append("lotes")

            cursor.execute("SELECT COUNT(*) FROM t_detalle_pedido WHERE det_pro_id_fk = %s", (pro_id,))
            if cursor.fetchone()[0] > 0:
                dependencias.append("detalles de pedidos")

            cursor.execute("SELECT COUNT(*) FROM t_detalle_compra WHERE dco_pro_id_fk = %s", (pro_id,))
            if cursor.fetchone()[0] > 0:
                dependencias.append("detalles de compras")

            cursor.execute("SELECT COUNT(*) FROM t_inventario_movimiento WHERE inm_pro_id_fk = %s", (pro_id,))
            if cursor.fetchone()[0] > 0:
                dependencias.append("movimientos de inventario")

            cursor.execute("SELECT COUNT(*) FROM t_monitoria WHERE mon_pro_id_fk = %s", (pro_id,))
            if cursor.fetchone()[0] > 0:
                dependencias.append("registros de monitoría")

            cursor.execute("SELECT COUNT(*) FROM t_alerta_vencimiento WHERE alv_pro_id_fk = %s", (pro_id,))
            if cursor.fetchone()[0] > 0:
                dependencias.append("alertas de vencimiento")

            cursor.execute("SELECT COUNT(*) FROM t_proveedor_producto WHERE ppp_pro_id_fk = %s", (pro_id,))
            if cursor.fetchone()[0] > 0:
                dependencias.append("relaciones proveedor-producto")

            if dependencias:
                cursor.close()
                return {
                    "ok": False,
                    "mensaje": f"No se puede eliminar el producto {pro_id} ({prod[0]}) porque tiene registros dependientes en: {', '.join(dependencias)}. Usa fuerza=true para eliminar en cascada."
                }, 409

            cursor.execute("DELETE FROM t_producto WHERE pro_id = %s", (pro_id,))
            current_app.mysql.connection.commit()
            filas = cursor.rowcount
            cursor.close()

            if filas == 0:
                return {"ok": False, "mensaje": "No se pudo eliminar el producto"}, 500

            return {"ok": True, "mensaje": f"Producto {pro_id} eliminado correctamente"}, 200

    except Exception as e:
        raise e


def editarProductos(pro_id, data):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            UPDATE t_producto
            SET pro_nombre=%s, pro_categoria=%s, pro_descripcion=%s, pro_precio=%s,
                pro_cantidad_disponible=%s, pro_stock_minimo=%s, pro_fecha_caducidad=%s,
                pro_registro_invima=%s, pro_fecha_vencimiento_registro=%s,
                pro_control_especial=%s, pro_tipo_control=%s, pro_estado=%s, pro_prov_id_fk=%s
            WHERE pro_id=%s
        """
        cursor.execute(sql, (
            data.get('nombre'), data.get('categoria'), data.get('descripcion'), data.get('precio'),
            data.get('cantidad_disponible'), data.get('stock_minimo', 10), data.get('fecha_caducidad'),
            data.get('registro_invima'), data.get('fecha_vencimiento_registro'),
            1 if data.get('control_especial') else 0, data.get('tipo_control'),
            data.get('estado', 'Activo'), data.get('proveedor_id'), pro_id
        ))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Producto actualizado correctamente"}
    except Exception as e:
        raise e
