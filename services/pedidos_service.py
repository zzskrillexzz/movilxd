from flask import current_app
from models.pedidos_model import pedidos
from services.notificaciones_service import enviar_email, generar_mensaje_factura_envio
from services.clientes_service import buscarClientes
from utils.search_builder import SearchBuilder
import base64

def listarPedidos(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_pedido',
        search_fields=['ped_id', 'ped_metodo_pago', 'ped_estado_entrega', 'ped_estado_pago'],
        exact_fields=['ped_estado_entrega', 'ped_estado_pago', 'ped_metodo_pago', 'ped_cli_id_fk', 'ped_usu_id_fk'],
        range_fields={'ped_fecha': 'date', 'ped_total': 'decimal'},
        default_order='ped_fecha DESC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    listav = []
    for item in result['data']:
        tiene = item.get('ped_comprobante_tipo') is not None
        ped = pedidos(
            ID=item['ped_id'], FECHA=item['ped_fecha'], METODO_DE_PAGO=item['ped_metodo_pago'],
            CUENTA_BANCARIA=item.get('ped_cuenta_bancaria'),
            ped_comprobante_tipo=item.get('ped_comprobante_tipo'),
            ESTADO=item['ped_estado_entrega'], TOTAL=item['ped_total'],
            ID_CLIENTE=item['ped_cli_id_fk'], ped_usu_id_fk=item.get('ped_usu_id_fk')
        ).a_diccionario()
        ped['ped_estado_pago'] = item.get('ped_estado_pago') or 'Pendiente de pago'
        ped['ped_tiene_comprobante'] = tiene
        ped['ped_token_entrega'] = item.get('ped_token_entrega')
        ped['ped_notificado'] = bool(item.get('ped_notificado')) if item.get('ped_notificado') is not None else False
        ped['ped_factura_enviada'] = bool(item.get('ped_factura_enviada')) if item.get('ped_factura_enviada') is not None else False
        listav.append(ped)

    result['data'] = listav
    return result

def registrarPedidos(ID, FECHA, METODO_DE_PAGO, ESTADO, TOTAL, ID_CLIENTE, ped_cuenta_bancaria=None, ped_comprobante=None, ped_comprobante_tipo=None, ped_usu_id_fk=None):
    c = current_app.mysql.connection.cursor()
    comprobante_bin = base64.b64decode(ped_comprobante) if ped_comprobante else None
    sql = "INSERT INTO t_pedido (ped_id, ped_fecha, ped_metodo_pago, ped_cuenta_bancaria, ped_comprobante, ped_comprobante_tipo, ped_estado_entrega, ped_estado_pago, ped_total, ped_cli_id_fk, ped_usu_id_fk) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    c.execute(sql, (ID, FECHA, METODO_DE_PAGO, ped_cuenta_bancaria, comprobante_bin, ped_comprobante_tipo, ESTADO, 'Pendiente de pago', TOTAL, ID_CLIENTE, ped_usu_id_fk))
    current_app.mysql.connection.commit()
    c.close()
    return pedidos(ID, FECHA, METODO_DE_PAGO, ped_cuenta_bancaria, ped_comprobante_tipo, ESTADO, TOTAL, ID_CLIENTE, ped_usu_id_fk).a_diccionario()

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
    return pedidos(ID, FECHA, METODO_DE_PAGO, ped_cuenta_bancaria, None, ESTADO, TOTAL, ID_CLIENTE, ped_usu_id_fk).a_diccionario()

def verificarPago(id, nuevo_estado):
    estados_validos = ['Verificado', 'Rechazado']
    if nuevo_estado not in estados_validos:
        raise ValueError(f"Estado inválido. Debe ser uno de: {estados_validos}")
    c = current_app.mysql.connection.cursor()
    if nuevo_estado == 'Verificado':
        c.execute("UPDATE t_pedido SET ped_estado_pago=%s, ped_estado_entrega=%s WHERE ped_id=%s",
                   (nuevo_estado, 'En preparación', id))
    else:
        c.execute("UPDATE t_pedido SET ped_estado_pago=%s WHERE ped_id=%s", (nuevo_estado, id))
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    return filas > 0

def avanzarEstado(id):
    import uuid
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT ped_estado_entrega FROM t_pedido WHERE ped_id = %s", (id,))
    r = c.fetchone()
    if not r:
        c.close()
        return None

    estado_actual = r[0]
    transiciones = {
        'En preparación': 'En camino',
        'En camino': 'Entregado'
    }

    if estado_actual not in transiciones:
        c.close()
        raise ValueError(f"El estado actual '{estado_actual}' no permite avanzar")

    nuevo_estado = transiciones[estado_actual]

    if nuevo_estado == 'En camino':
        # Generar token único para QR de confirmación de entrega
        token = uuid.uuid4().hex
        c.execute("UPDATE t_pedido SET ped_estado_entrega = %s, ped_token_entrega = %s WHERE ped_id = %s",
                   (nuevo_estado, token, id))
    else:
        c.execute("UPDATE t_pedido SET ped_estado_entrega = %s WHERE ped_id = %s",
                   (nuevo_estado, id))

    current_app.mysql.connection.commit()
    c.close()
    return buscarPedido(id)


def obtenerTokenEntrega(id):
    """Obtiene el token de confirmación de entrega de un pedido."""
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT ped_token_entrega FROM t_pedido WHERE ped_id = %s", (id,))
    r = c.fetchone()
    c.close()
    return r[0] if r else None


def confirmarEntregaPorToken(token):
    """
    Confirma la entrega de un pedido usando su token único.
    Retorna el pedido actualizado o None si el token es inválido.
    """
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT ped_id, ped_estado_entrega FROM t_pedido WHERE ped_token_entrega = %s", (token,))
    r = c.fetchone()
    if not r:
        c.close()
        return None

    ped_id, estado_actual = r

    if estado_actual != 'En camino':
        c.close()
        raise ValueError(f"El pedido {ped_id} no está en camino (estado actual: {estado_actual})")

    c.execute("UPDATE t_pedido SET ped_estado_entrega = 'Entregado' WHERE ped_id = %s", (ped_id,))
    current_app.mysql.connection.commit()
    c.close()
    return buscarPedido(ped_id)

def subirComprobante(id, comprobante_b64, comprobante_tipo):
    c = current_app.mysql.connection.cursor()
    comprobante_bin = base64.b64decode(comprobante_b64) if comprobante_b64 else None
    c.execute(
        "UPDATE t_pedido SET ped_comprobante=%s, ped_comprobante_tipo=%s, ped_estado_pago=%s WHERE ped_id=%s",
        (comprobante_bin, comprobante_tipo, 'Comprobante recibido', id)
    )
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    if filas == 0:
        return None
    return buscarPedido(id)

def enviarFacturaEmail(id):
    """Envía la factura del pedido por email al cliente."""
    pedido = buscarPedido(id)
    if not pedido:
        return {'ok': False, 'error': 'Pedido no encontrado'}

    cliente = buscarClientes(pedido.get('ped_cli_id_fk'))
    if not cliente:
        return {'ok': False, 'error': 'Cliente no encontrado'}

    email = cliente.get('cli_correo')
    if not email:
        return {'ok': False, 'error': 'El cliente no tiene correo registrado'}

    asunto, html, _ = generar_mensaje_factura_envio(pedido, cliente)
    resultado = enviar_email(email, asunto, html)

    if resultado.get('ok'):
        return {'ok': True, 'mensaje': f'Factura enviada a {email}'}
    return {'ok': False, 'error': resultado.get('error', 'Error al enviar email')}


def marcarNotificado(id):
    """Marca que la notificación fue enviada al cliente."""
    c = current_app.mysql.connection.cursor()
    c.execute("UPDATE t_pedido SET ped_notificado = 1 WHERE ped_id = %s", (id,))
    current_app.mysql.connection.commit()
    c.close()


def marcarFacturaEnviada(id):
    """Marca que la factura fue enviada al correo del cliente."""
    c = current_app.mysql.connection.cursor()
    c.execute("UPDATE t_pedido SET ped_factura_enviada = 1 WHERE ped_id = %s", (id,))
    # Intentar actualizar email_enviado y fac_cli_id_fk; si la columna no existe, solo email_enviado
    try:
        c.execute("""
            UPDATE t_factura f
            JOIN t_pedido p ON f.fac_id = p.ped_id
            SET f.fac_email_enviado = 1, f.fac_cli_id_fk = p.ped_cli_id_fk
            WHERE f.fac_id = %s
        """, (id,))
    except Exception:
        c.execute("UPDATE t_factura SET fac_email_enviado = 1 WHERE fac_id = %s", (id,))
    current_app.mysql.connection.commit()
    c.close()


def revertirInventarioPedido(ped_id):
    """
    Revierte el inventario de todos los detalles de un pedido:
    reingresa stock a productos y lotes, y registra movimientos de Entrada + monitoria.
    """
    from utils.id_generator import generarIdSiguiente

    c = current_app.mysql.connection.cursor()

    # Obtener todos los detalles del pedido
    c.execute("SELECT det_id, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal FROM t_detalle_pedido WHERE det_ped_id_fk = %s", (ped_id,))
    detalles = c.fetchall()

    for det in detalles:
        det_id, det_pro_id_fk, det_lot_id_fk, det_cantidad, det_precio_unitario, det_subtotal = det

        # Reingresar stock al producto (BUG-009: UPDATE atómico)
        c.execute(
            "UPDATE t_producto SET pro_cantidad_disponible = pro_cantidad_disponible + %s "
            "WHERE pro_id = %s",
            (det_cantidad, det_pro_id_fk)
        )
        c.execute("SELECT pro_cantidad_disponible FROM t_producto WHERE pro_id = %s", (det_pro_id_fk,))
        row = c.fetchone()
        if row:
            nuevo_stock = row[0] or 0
            stock_anterior = nuevo_stock - det_cantidad
        else:
            stock_anterior = 0
            nuevo_stock = det_cantidad

        # Reingresar stock al lote si aplica
        if det_lot_id_fk:
            c.execute("SELECT lot_cantidad_actual, lot_estado FROM t_lote WHERE lot_id = %s", (det_lot_id_fk,))
            row_lote = c.fetchone()
            if row_lote:
                stock_lote_anterior = row_lote[0] or 0
                nuevo_stock_lote = stock_lote_anterior + det_cantidad
                c.execute("UPDATE t_lote SET lot_cantidad_actual = %s WHERE lot_id = %s", (nuevo_stock_lote, det_lot_id_fk))
                if row_lote[1] == 'Agotado' and nuevo_stock_lote > 0:
                    c.execute("UPDATE t_lote SET lot_estado = 'Activo' WHERE lot_id = %s", (det_lot_id_fk,))

        # Movimiento de inventario (Entrada por reversión)
        inm_id = generarIdSiguiente('t_inventario_movimiento', 'inm_id', 'INM', 3)
        c.execute("""
            INSERT INTO t_inventario_movimiento (inm_id, inm_tipo_movimiento, inm_pro_id_fk, inm_lot_id_fk, inm_cantidad, inm_fecha, inm_motivo, inm_usu_id_fk)
            VALUES (%s, 'Entrada', %s, %s, %s, CURDATE(), %s, NULL)
        """, (inm_id, det_pro_id_fk, det_lot_id_fk, det_cantidad, f"Anulacion venta {ped_id}"))

        # Monitoria
        mon_id = generarIdSiguiente('t_monitoria', 'mon_id', 'MON', 3)
        costo_total = det_cantidad * (float(det_precio_unitario) if det_precio_unitario else 0)
        c.execute("""
            INSERT INTO t_monitoria (mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo,
                                     mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total)
            VALUES (%s, %s, %s, %s, CURDATE(), 'Entrada', %s, %s, %s, %s, %s)
        """, (mon_id, det_pro_id_fk, det_lot_id_fk, inm_id, det_cantidad, stock_anterior, nuevo_stock,
              float(det_precio_unitario) if det_precio_unitario else 0, costo_total))

    # Eliminar los detalles ya revertidos
    c.execute("DELETE FROM t_detalle_pedido WHERE det_ped_id_fk = %s", (ped_id,))
    current_app.mysql.connection.commit()
    c.close()


def eliminarPedidos(ID):
    c = current_app.mysql.connection.cursor()

    # Verificar si tiene detalles y revertir inventario antes de eliminar
    c.execute("SELECT det_id FROM t_detalle_pedido WHERE det_ped_id_fk=%s LIMIT 1", (ID,))
    if c.fetchone():
        c.close()
        # Revertir inventario de los detalles y eliminarlos
        revertirInventarioPedido(ID)
        c = current_app.mysql.connection.cursor()

    c.execute("DELETE FROM t_pedido WHERE ped_id=%s", (ID,))
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    return filas > 0

def buscarPedido(ID):
    c = current_app.mysql.connection.cursor()
    sql = """SELECT ped_id, ped_fecha, ped_metodo_pago, ped_cuenta_bancaria, ped_comprobante, ped_comprobante_tipo, ped_estado_entrega, ped_estado_pago, ped_total, ped_cli_id_fk, ped_usu_id_fk, ped_token_entrega, ped_notificado, ped_factura_enviada FROM t_pedido WHERE ped_id=%s"""
    c.execute(sql, (ID,))
    r = c.fetchone()
    c.close()
    if r:
        tiene = r[5] is not None
        ped = pedidos(ID=r[0], FECHA=r[1], METODO_DE_PAGO=r[2], CUENTA_BANCARIA=r[3], ped_comprobante=r[4], ped_comprobante_tipo=r[5], ESTADO=r[6], TOTAL=r[8], ID_CLIENTE=r[9], ped_usu_id_fk=r[10]).a_diccionario()
        ped['ped_estado_pago'] = r[7] or 'Pendiente de pago'
        ped['ped_tiene_comprobante'] = tiene
        ped['ped_token_entrega'] = r[11]
        ped['ped_notificado'] = bool(r[12]) if len(r) > 12 else False
        ped['ped_factura_enviada'] = bool(r[13]) if len(r) > 13 else False
        return ped
    return None
