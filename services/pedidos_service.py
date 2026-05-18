from flask import current_app
from models.pedidos_model import pedidos
from services.notificaciones_service import enviar_email, generar_mensaje_factura_envio
from services.clientes_service import buscarClientes
import base64

def listarPedidos():
    c = current_app.mysql.connection.cursor()
    sql = "SELECT ped_id, ped_fecha, ped_metodo_pago, ped_cuenta_bancaria, ped_comprobante_tipo, ped_estado_entrega, ped_estado_pago, ped_total, ped_cli_id_fk, ped_usu_id_fk, ped_token_entrega FROM t_pedido"
    c.execute(sql)
    reg = c.fetchall()
    listav = []
    for p in reg:
        tiene = p[4] is not None
        ped = pedidos(
            ID=p[0], FECHA=p[1], METODO_DE_PAGO=p[2], CUENTA_BANCARIA=p[3],
            ped_comprobante_tipo=p[4],
            ESTADO=p[5], TOTAL=p[7], ID_CLIENTE=p[8], ped_usu_id_fk=p[9]
        ).a_diccionario()
        ped['ped_estado_pago'] = p[6] or 'Pendiente de pago'
        ped['ped_tiene_comprobante'] = tiene
        ped['ped_token_entrega'] = p[10]
        listav.append(ped)
    return listav

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


def eliminarPedidos(ID):
    c = current_app.mysql.connection.cursor()
    c.execute("DELETE FROM t_pedido WHERE ped_id=%s", (ID,))
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    return filas > 0

def buscarPedido(ID):
    c = current_app.mysql.connection.cursor()
    sql = """SELECT ped_id, ped_fecha, ped_metodo_pago, ped_cuenta_bancaria, ped_comprobante, ped_comprobante_tipo, ped_estado_entrega, ped_estado_pago, ped_total, ped_cli_id_fk, ped_usu_id_fk, ped_token_entrega FROM t_pedido WHERE ped_id=%s"""
    c.execute(sql, (ID,))
    r = c.fetchone()
    c.close()
    if r:
        tiene = r[5] is not None
        ped = pedidos(ID=r[0], FECHA=r[1], METODO_DE_PAGO=r[2], CUENTA_BANCARIA=r[3], ped_comprobante=r[4], ped_comprobante_tipo=r[5], ESTADO=r[6], TOTAL=r[8], ID_CLIENTE=r[9], ped_usu_id_fk=r[10]).a_diccionario()
        ped['ped_estado_pago'] = r[7] or 'Pendiente de pago'
        ped['ped_tiene_comprobante'] = tiene
        ped['ped_token_entrega'] = r[11]
        return ped
    return None
