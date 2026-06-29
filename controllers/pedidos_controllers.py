from flask import jsonify, request, current_app, render_template_string, g
from services.pedidos_service import (
    listarPedidos, registrarPedidos,
    editarPedidos, eliminarPedidos, buscarPedido, verificarPago,
    subirComprobante, avanzarEstado, enviarFacturaEmail,
    confirmarEntregaPorToken, marcarNotificado, marcarFacturaEnviada
)
from utils.id_generator import generarIdSiguiente
from utils.validators import validar_campos_texto
from utils.error_handler import safe_controller
from utils.logger import get_logger

log = get_logger(__name__)
from services.clientes_service import buscarClientes
from services.notificaciones_service import enviar_email, enviar_whatsapp, generar_mensaje_pedido_listo

@safe_controller
def cnlistadopedidos():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    x = listarPedidos(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(x), 200

def cnregistrarpedidos():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        requerido = ["ped_fecha", "ped_metodo_pago", "ped_estado_entrega", "ped_total", "ped_cli_id_fk"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        # Generar ID auto si no se envio
        ped_id = data.get("ped_id") or generarIdSiguiente("t_pedido", "ped_id", "PED", 3)

        # Validar campos no vacíos
        for campo in ["ped_fecha", "ped_metodo_pago", "ped_estado_entrega"]:
            if str(data[campo]).strip() == "":
                return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

        # Validar que la fecha no sea anterior a hoy
        from datetime import date
        try:
            fecha_pedido = data["ped_fecha"]
            # Intentar parsear la fecha en formato YYYY-MM-DD
            if isinstance(fecha_pedido, str):
                año, mes, dia = map(int, fecha_pedido.split("-"))
                fecha_pedido_obj = date(año, mes, dia)
            else:
                return jsonify({"mensaje": "El formato de ped_fecha no es válido (use YYYY-MM-DD)"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El formato de ped_fecha no es válido (use YYYY-MM-DD)"}), 400

        if fecha_pedido_obj < date.today():
            return jsonify({"mensaje": "No se pueden crear pedidos en fechas pasadas. La fecha debe ser hoy o posterior."}), 400

        # Validar longitud de campos de texto opcionales
        errores = validar_campos_texto(data, "ped_cuenta_bancaria", "ped_comprobante_tipo")
        if errores:
            return jsonify({"mensaje": " | ".join(errores)}), 400

        # Validar método de pago
        metodos_validos = ["Efectivo", "Tarjeta", "Transferencia", "Nequi", "Daviplata"]
        if data["ped_metodo_pago"] not in metodos_validos:
            return jsonify({"mensaje": f"Método de pago inválido. Valores permitidos: {metodos_validos}"}), 400

        # Validar cuenta bancaria requerida si es transferencia
        if data.get("ped_metodo_pago") == "Transferencia" and (not data.get("ped_cuenta_bancaria") or str(data["ped_cuenta_bancaria"]).strip() == ""):
            return jsonify({"mensaje": "Debe seleccionar un banco o billetera cuando el método de pago es Transferencia"}), 400

        # Validar cuenta bancaria (solo bancos permitidos)
        BANCOS_PERMITIDOS = [
            "Bancolombia", "Davivienda", "Banco de Bogotá", "BBVA Colombia",
            "Banco de Occidente", "Banco Popular", "Banco Agrario", "Banco Caja Social",
            "Banco Falabella", "Scotiabank Colpatria", "Itaú Colombia", "Banco Pichincha",
            "Bancamía", "Bancoomeva", "AV Villas", "Nequi", "Daviplata", "Movii", "Dale"
        ]
        if data.get("ped_cuenta_bancaria") and data["ped_cuenta_bancaria"] not in BANCOS_PERMITIDOS:
            return jsonify({"mensaje": "Cuenta bancaria no válida. Seleccione una de la lista."}), 400

        # Validar estado entrega
        estados_validos = ["Pendiente", "En preparación", "En camino", "Entregado", "Anulado"]
        if data["ped_estado_entrega"] not in estados_validos:
            return jsonify({"mensaje": f"Estado de entrega inválido. Valores permitidos: {estados_validos}"}), 400

        # Validar total positivo
        try:
            total = float(data["ped_total"])
            if total <= 0:
                return jsonify({"mensaje": "El total debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El total debe ser un número válido"}), 400

        # Validar que ped_cli_id_fk sea un entero positivo
        try:
            cli_id_fk = int(data["ped_cli_id_fk"])
            if cli_id_fk <= 0:
                return jsonify({"mensaje": "El ID del cliente debe ser un número positivo"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El ID del cliente debe ser un número entero"}), 400

        # Validar duplicado — si existe pero está vacío (sin detalles), eliminarlo y continuar
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT ped_id FROM t_pedido WHERE ped_id = %s", (ped_id,))
        existing = c.fetchone()
        if existing:
            # Verificar si el pedido existente tiene detalles
            c.execute("SELECT COUNT(*) FROM t_detalle_pedido WHERE det_ped_id_fk = %s", (ped_id,))
            tiene_detalles = c.fetchone()[0] > 0
            if tiene_detalles:
                c.close()
                return jsonify({"mensaje": f"Ya existe un pedido con el ID {ped_id} y tiene productos asociados"}), 409
            # Pedido huérfano (sin detalles) — eliminarlo y permitir la creación
            c.execute("DELETE FROM t_pedido WHERE ped_id = %s", (ped_id,))
            current_app.mysql.connection.commit()

        # Validar que el cliente exista
        c.execute("SELECT cli_id FROM t_cliente WHERE cli_id = %s", (data["ped_cli_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un cliente con el ID {data['ped_cli_id_fk']}"}), 404

        # Validar que el usuario exista (si se envía)
        fk_usuario = data.get("ped_usu_id_fk")
        if fk_usuario:
            c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (fk_usuario,))
            if not c.fetchone():
                c.close()
                return jsonify({"mensaje": f"No existe un usuario con el ID {fk_usuario}"}), 404
        c.close()

        # Validar cuarentena en productos seleccionados (si se enviaron)
        productos = data.get("productos")
        if productos and isinstance(productos, list) and len(productos) > 0:
            c2 = current_app.mysql.connection.cursor()
            try:
                for prod in productos:
                    pro_id = prod.get("pro_id") if isinstance(prod, dict) else prod
                    if not pro_id:
                        continue
                    # Verificar si todos los lotes con stock disponible están en cuarentena
                    c2.execute("""
                        SELECT
                          CASE WHEN COUNT(*) > 0 AND SUM(CASE WHEN lot_estado != 'Cuarentena' THEN 1 ELSE 0 END) = 0
                          THEN 1 ELSE 0 END as solo_cuarentena
                        FROM t_lote
                        WHERE lot_pro_id_fk = %s AND lot_cantidad_actual > 0
                    """, (pro_id,))
                    row = c2.fetchone()
                    if row and row[0] == 1:
                        c2.close()
                        return jsonify({
                            "mensaje": f"El producto {pro_id} solo tiene lotes en CUARENTENA. "
                                       "No se puede crear el pedido con productos en cuarentena."
                        }), 400
            finally:
                c2.close()

        # Calcular IVA (19%) si no se envía explícitamente
        total = float(data["ped_total"])
        ped_subtotal = data.get("ped_subtotal")
        ped_iva = data.get("ped_iva")
        if ped_subtotal is not None and ped_iva is None:
            ped_iva = round(float(ped_subtotal) * 0.19, 2)
        elif ped_subtotal is None and ped_iva is None:
            ped_subtotal = round(total / 1.19, 2)
            ped_iva = round(total - ped_subtotal, 2)

        resultado = registrarPedidos(
            ped_id, data["ped_fecha"], data["ped_metodo_pago"],
            data["ped_estado_entrega"], data["ped_total"], data["ped_cli_id_fk"],
            data.get("ped_cuenta_bancaria"),
            data.get("ped_comprobante"),
            data.get("ped_comprobante_tipo"),
            fk_usuario
        )
        # Agregar desglose de IVA en la respuesta
        if isinstance(resultado, dict):
            resultado["ped_subtotal"] = ped_subtotal
            resultado["ped_iva"] = ped_iva
            resultado["ped_iva_porcentaje"] = 19
        return jsonify({
            "mensaje": "Pedido realizado correctamente",
            "datos": resultado,
            "desglose_iva": {
                "subtotal": ped_subtotal,
                "iva_19pct": ped_iva,
                "total": total
            }
        }), 201

    except Exception as e:
        log.error(f"Error en registrarPedidos: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@safe_controller
def cnbuscarpedido(id):
    pedido = buscarPedido(id)
    if not pedido:
        return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404
    return jsonify(pedido), 200

def cnsubircomprobante(id):
    try:
        data = request.get_json()
        if not data or not data.get("ped_comprobante") or not data.get("ped_comprobante_tipo"):
            return jsonify({"mensaje": "Debe enviar ped_comprobante (base64) y ped_comprobante_tipo"}), 400

        resultado = subirComprobante(
            id, data["ped_comprobante"], data["ped_comprobante_tipo"]
        )
        if resultado is None:
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404
        return jsonify({"mensaje": "Comprobante subido correctamente", "datos": resultado}), 200

    except Exception as e:
        log.error(f"Error en subirComprobante: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def cndescargarcomprobante(id):
    """Retorna el archivo de comprobante — soporta tanto blob en DB como archivo en disco."""
    try:
        import os
        import base64 as b64
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT ped_comprobante, ped_comprobante_tipo FROM t_pedido WHERE ped_id = %s", (id,))
        r = c.fetchone()
        c.close()
        if not r or not r[0] or not r[1]:
            return jsonify({"mensaje": "No hay comprobante para este pedido"}), 404

        dato = r[0]
        mime = r[1]

        # Determinar si es un nombre de archivo en disco
        es_filename = False
        filename = None
        if isinstance(dato, str):
            # String: si es corto (< 100 chars) y no parece base64, es filename
            if len(dato) < 100:
                es_filename = True
                filename = dato
        elif isinstance(dato, bytes):
            # Bytes: si es corto y decodifica como ASCII limpio, es filename
            if len(dato) < 150:
                try:
                    decoded = dato.decode('ascii')
                    if len(decoded) < 100 and not any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-.{}' for c in decoded):
                        es_filename = True
                        filename = decoded
                except Exception:
                    pass

        if es_filename:
            upload_dir = current_app.config.get('COMPROBANTES_DIR', os.path.join(current_app.root_path, 'comprobantes'))
            filepath = os.path.join(upload_dir, filename)
            if not os.path.exists(filepath):
                return jsonify({"mensaje": "El archivo de comprobante no existe en el servidor"}), 404
            from flask import send_file
            return send_file(filepath, mimetype=mime)

        # Datos legacy guardados en la DB (blob o base64)
        if isinstance(dato, bytes):
            # Puede ser binario puro (blob) o base64 texto en bytes
            if dato[:4] == b'\x89PNG' or dato[:2] == b'\xff\xd8' or dato[:4] == b'%PDF':
                binary = dato
            else:
                try:
                    binary = b64.b64decode(dato)
                except Exception:
                    binary = dato
        else:
            # String largo: es base64 texto
            try:
                binary = b64.b64decode(dato)
            except Exception:
                binary = dato.encode('latin-1')
        return current_app.response_class(binary, mimetype=mime)
    except Exception as e:
        log.error(f"Error al descargar comprobante: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def cnavanzarestado(id):
    try:
        pedido = buscarPedido(id)
        if not pedido:
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        resultado = avanzarEstado(id)
        if resultado is None:
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404
        return jsonify({"mensaje": "Estado avanzado correctamente", "datos": resultado}), 200

    except ValueError as e:
        return jsonify({"mensaje": str(e)}), 400
    except Exception as e:
        log.error(f"Error en avanzarEstado: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def cnenviarfactura(id):
    try:
        pedido = buscarPedido(id)
        if not pedido:
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        resultado = enviarFacturaEmail(id)
        if resultado.get('ok'):
            marcarFacturaEnviada(id)
            return jsonify(resultado), 200
        return jsonify(resultado), 400

    except Exception as e:
        log.error(f"Error en enviarFactura: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def cneditarpedidos(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        # Verificar que el pedido exista
        if not buscarPedido(id):
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        requerido = ["ped_fecha", "ped_metodo_pago", "ped_estado_entrega", "ped_total", "ped_cli_id_fk"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        # Validar formato de fecha — también bloqueamos fechas pasadas en edición
        from datetime import date
        try:
            fecha_pedido = data["ped_fecha"]
            if isinstance(fecha_pedido, str):
                año, mes, dia = map(int, fecha_pedido.split("-"))
                fecha_obj = date(año, mes, dia)
                if fecha_obj < date.today():
                    return jsonify({"mensaje": "No se pueden crear pedidos en fechas pasadas. La fecha debe ser hoy o posterior."}), 400
            else:
                return jsonify({"mensaje": "El formato de ped_fecha no es válido (use YYYY-MM-DD)"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El formato de ped_fecha no es válido (use YYYY-MM-DD)"}), 400

        # Validar longitud de campos de texto opcionales
        errores = validar_campos_texto(data, "ped_cuenta_bancaria", "ped_comprobante_tipo")
        if errores:
            return jsonify({"mensaje": " | ".join(errores)}), 400

        metodos_validos = ["Efectivo", "Tarjeta", "Transferencia", "Nequi", "Daviplata"]
        if data["ped_metodo_pago"] not in metodos_validos:
            return jsonify({"mensaje": f"Método de pago inválido. Valores permitidos: {metodos_validos}"}), 400

        # Validar cuenta bancaria requerida si es transferencia
        if data.get("ped_metodo_pago") == "Transferencia" and (not data.get("ped_cuenta_bancaria") or str(data["ped_cuenta_bancaria"]).strip() == ""):
            return jsonify({"mensaje": "Debe seleccionar un banco o billetera cuando el método de pago es Transferencia"}), 400

        # Validar cuenta bancaria (solo bancos permitidos)
        BANCOS_PERMITIDOS = [
            "Bancolombia", "Davivienda", "Banco de Bogotá", "BBVA Colombia",
            "Banco de Occidente", "Banco Popular", "Banco Agrario", "Banco Caja Social",
            "Banco Falabella", "Scotiabank Colpatria", "Itaú Colombia", "Banco Pichincha",
            "Bancamía", "Bancoomeva", "AV Villas", "Nequi", "Daviplata", "Movii", "Dale"
        ]
        if data.get("ped_cuenta_bancaria") and data["ped_cuenta_bancaria"] not in BANCOS_PERMITIDOS:
            return jsonify({"mensaje": "Cuenta bancaria no válida. Seleccione una de la lista."}), 400

        estados_validos = ["Pendiente", "En preparación", "En camino", "Entregado", "Anulado"]
        if data["ped_estado_entrega"] not in estados_validos:
            return jsonify({"mensaje": f"Estado de entrega inválido. Valores permitidos: {estados_validos}"}), 400

        try:
            total = float(data["ped_total"])
            if total <= 0:
                return jsonify({"mensaje": "El total debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El total debe ser un número válido"}), 400

        # Validar que ped_cli_id_fk sea un entero positivo
        try:
            cli_id_fk = int(data["ped_cli_id_fk"])
            if cli_id_fk <= 0:
                return jsonify({"mensaje": "El ID del cliente debe ser un número positivo"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El ID del cliente debe ser un número entero"}), 400

        c = current_app.mysql.connection.cursor()
        c.execute("SELECT cli_id FROM t_cliente WHERE cli_id=%s", (data["ped_cli_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un cliente con el ID {data['ped_cli_id_fk']}"}), 404

        fk_usuario = data.get("ped_usu_id_fk")
        if fk_usuario:
            c.execute("SELECT usu_id FROM t_usuario WHERE usu_id=%s", (fk_usuario,))
            if not c.fetchone():
                c.close()
                return jsonify({"mensaje": f"No existe un usuario con el ID {fk_usuario}"}), 404
        c.close()

        resultado = editarPedidos(
            id, data["ped_fecha"], data["ped_metodo_pago"], data["ped_estado_entrega"],
            data["ped_total"], data["ped_cli_id_fk"], fk_usuario
        )
        return jsonify({"mensaje": "Pedido actualizado correctamente", "datos": resultado}), 200

    except Exception as e:
        log.error(f"Error en editarPedidos: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def cneverificarpago(id):
    try:
        pedido = buscarPedido(id)
        if not pedido:
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        if pedido.get('ped_estado_pago') == 'Verificado':
            return jsonify({"mensaje": "El pago ya fue verificado, no se puede cambiar el estado"}), 400

        data = request.get_json()
        if not data or 'estado_pago' not in data:
            return jsonify({"mensaje": "El campo 'estado_pago' es requerido (Verificado / Rechazado)"}), 400

        estado = data['estado_pago']
        if estado not in ['Verificado', 'Rechazado']:
            return jsonify({"mensaje": "Estado inválido. Debe ser 'Verificado' o 'Rechazado'"}), 400

        ok = verificarPago(id, estado)
        if ok:
            # Si se verificó el pago, crear la factura automáticamente
            factura_creada = None
            if estado == 'Verificado':
                try:
                    from services.facturas_service import buscarFacturas, registrarFacturas
                    from datetime import datetime
                    from zoneinfo import ZoneInfo
                    factura_existente = buscarFacturas(id)
                    if not factura_existente:
                        # Usar el usuario logueado como fallback si ped_usu_id_fk es NULL
                        usuario_id = pedido.get('ped_usu_id_fk')
                        if not usuario_id:
                            usuario_id = g.get('usuario_actual', {}).get('id') if hasattr(g, 'usuario_actual') else None
                        factura_data = {
                            'id': id,
                            'fecha_emision': pedido.get('ped_fecha') or datetime.now(ZoneInfo("America/Bogota")).strftime('%Y-%m-%d %H:%M:%S'),
                            'email_enviado': 0,
                            'forma_pago': pedido.get('ped_metodo_pago', ''),
                            'cuenta_bancaria': pedido.get('ped_cuenta_bancaria', ''),
                            'total': pedido.get('ped_total', 0),
                            'usuario_id': usuario_id,
                            'estado': 'Vigente',
                            'cli_id_fk': pedido.get('ped_cli_id_fk')
                        }
                        registrarFacturas(factura_data)
                        factura_creada = True
                except Exception as e:
                    # La factura no es crítica, reportar pero no fallar
                    log.error(f"Error al crear factura automática para pedido {id}: {e}")
                    factura_creada = str(e)

            # Si se rechazó el pago, revertir el inventario
            inventario_revertido = None
            if estado == 'Rechazado':
                try:
                    from services.pedidos_service import revertirInventarioPedido
                    revertirInventarioPedido(id)
                    inventario_revertido = True
                except Exception as e:
                    print(f"Error al revertir inventario para pedido {id}: {e}")
                    inventario_revertido = str(e)

            return jsonify({
                "mensaje": f"Pago del pedido {id} marcado como {estado}",
                "ped_estado_pago": estado,
                "factura_creada": factura_creada,
                "inventario_revertido": inventario_revertido
            }), 200
        return jsonify({"mensaje": "No se pudo actualizar el estado del pago"}), 500

    except Exception as e:
        log.error(f"Error en verificarPago: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def cnnotificarpedido(id):
    try:
        pedido = buscarPedido(id)
        if not pedido:
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        if pedido.get('ped_estado_pago') != 'Verificado':
            return jsonify({"mensaje": "El pago debe estar Verificado antes de notificar al cliente"}), 400

        data = request.get_json() or {}
        medio = data.get('medio', 'ambos')  # 'email', 'whatsapp', 'ambos'

        # Obtener datos del cliente
        cliente_id = pedido.get('ped_cli_id_fk')
        cliente = buscarClientes(cliente_id)
        if not cliente:
            return jsonify({"mensaje": f"No se encontró el cliente con ID {cliente_id}"}), 404

        asunto, html, texto_wa = generar_mensaje_pedido_listo(pedido, cliente)

        resultados = {}

        if medio in ('email', 'ambos'):
            email_dest = cliente.get('cli_correo')
            if email_dest:
                resultados['email'] = enviar_email(email_dest, asunto, html)
                if resultados['email'].get('ok'):
                    marcarNotificado(id)
            else:
                resultados['email'] = {'ok': False, 'error': 'El cliente no tiene correo registrado'}

        if medio in ('whatsapp', 'ambos'):
            tel = cliente.get('cli_telefono')
            if tel:
                resultados['whatsapp'] = enviar_whatsapp(tel, texto_wa)
            else:
                resultados['whatsapp'] = {'ok': False, 'error': 'El cliente no tiene teléfono registrado'}

        return jsonify({
            "mensaje": "Notificación procesada",
            "resultados": resultados,
            "cliente": {
                "nombre": f"{cliente.get('cli_nombre', '')} {cliente.get('cli_apellido', '')}",
                "correo": cliente.get('cli_correo'),
                "telefono": cliente.get('cli_telefono')
            }
        }), 200

    except Exception as e:
        log.error(f"Error en notificarPedido: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def cneliminarpedidos(id):
    try:
        if not buscarPedido(id):
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        # eliminarPedidos ahora revierte el inventario automáticamente si el pedido tiene detalles
        if eliminarPedidos(id):
            return jsonify({"mensaje": f"Pedido {id} eliminado correctamente (inventario revertido)"}), 200
        return jsonify({"mensaje": "No se pudo eliminar el pedido"}), 500

    except Exception as e:
        log.error(f"Error en eliminarPedidos: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


PAGINA_CONFIRMACION = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmar entrega — San Diego Distribuidora</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f1f5f9;
            display: flex; align-items: center; justify-content: center;
            min-height: 100vh; padding: 20px;
        }
        .card {
            background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 40px; max-width: 420px; width: 100%; text-align: center;
        }
        .icono { font-size: 64px; margin-bottom: 16px; }
        h1 { font-size: 24px; color: #0f172a; margin-bottom: 8px; }
        .pedido-id { font-size: 14px; color: #64748b; margin-bottom: 24px; }
        .pedido-id strong { color: #0f172a; }
        .estado { display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 24px; }
        .estado-camino { background: #fef3c7; color: #92400e; }
        .estado-entregado { background: #dcfce7; color: #166534; }
        .estado-error { background: #fee2e2; color: #991b1b; }
        .btn {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 14px 32px; border: none; border-radius: 12px;
            font-size: 16px; font-weight: 700; cursor: pointer;
            transition: all 0.2s; text-decoration: none;
        }
        .btn-primary { background: #059669; color: white; }
        .btn-primary:hover { background: #047857; transform: translateY(-1px); }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .btn-success { background: #dcfce7; color: #166534; cursor: default; }
        .btn-error { background: #fee2e2; color: #991b1b; cursor: default; }
        .mensaje { margin-top: 16px; font-size: 14px; color: #64748b; }
        .footer { margin-top: 24px; font-size: 12px; color: #94a3b8; }
        @media (max-width: 480px) {
            .card { padding: 24px; }
            h1 { font-size: 20px; }
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="icono">{{ icono }}</div>
        <h1>{{ titulo }}</h1>
        <p class="pedido-id">Pedido: <strong>{{ pedido_id }}</strong></p>
        <div class="estado {{ estado_clase }}">{{ estado_texto }}</div>
        {% if mostrar_boton %}
        <form method="POST">
            <button type="submit" class="btn btn-primary">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                Confirmar entrega
            </button>
        </form>
        <p class="mensaje">¿El pedido fue entregado al cliente?<br>Confirma para marcarlo como entregado.</p>
        {% endif %}
        {% if mensaje_final %}
        <p class="mensaje">{{ mensaje_final }}</p>
        {% endif %}
        <div class="footer">San Diego Distribuidora · Sistema de gestión de pedidos</div>
    </div>
</body>
</html>"""


def cnconfirmarentrega(token):
    """
    GET  → Muestra página de confirmación de entrega
    POST → Procesa la confirmación y marca como Entregado
    """
    from services.pedidos_service import confirmarEntregaPorToken

    try:
        pedido = None
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT ped_id, ped_estado_entrega FROM t_pedido WHERE ped_token_entrega = %s", (token,))
        r = c.fetchone()
        c.close()

        if request.method == 'POST':
            if not r:
                return render_template_string(PAGINA_CONFIRMACION,
                    icono='❌',
                    titulo='Token inválido',
                    pedido_id='---',
                    estado_clase='estado-error',
                    estado_texto='Token no reconocido',
                    mostrar_boton=False,
                    mensaje_final='El enlace de confirmación no es válido o ya expiró. Contacta al administrador.'
                ), 404

            pedido_id, estado_actual = r
            if estado_actual != 'En camino':
                estado_actual_legible = estado_actual
                return render_template_string(PAGINA_CONFIRMACION,
                    icono='⚠️',
                    titulo='Entrega ya procesada',
                    pedido_id=pedido_id,
                    estado_clase='estado-entregado' if estado_actual == 'Entregado' else 'estado-error',
                    estado_texto=f'Estado actual: {estado_actual}',
                    mostrar_boton=False,
                    mensaje_final=f'El pedido ya está marcado como "{estado_actual}". No es necesario repetir la confirmación.'
                )

            try:
                confirmarEntregaPorToken(token)
            except ValueError as e:
                return render_template_string(PAGINA_CONFIRMACION,
                    icono='⚠️',
                    titulo='Error',
                    pedido_id=pedido_id,
                    estado_clase='estado-error',
                    estado_texto=str(e),
                    mostrar_boton=False,
                    mensaje_final='Ocurrió un error al procesar la confirmación. Contacta al administrador.'
                ), 400

            return render_template_string(PAGINA_CONFIRMACION,
                icono='✅',
                titulo='¡Entrega confirmada!',
                pedido_id=pedido_id,
                estado_clase='estado-entregado',
                estado_texto='Entregado',
                mostrar_boton=False,
                mensaje_final='El pedido ha sido marcado como entregado exitosamente. ¡Gracias!'
            )

        # GET - mostrar página de confirmación
        if not r:
            return render_template_string(PAGINA_CONFIRMACION,
                icono='❌',
                titulo='Token inválido',
                pedido_id='---',
                estado_clase='estado-error',
                estado_texto='No reconocido',
                mostrar_boton=False,
                mensaje_final='El enlace no es válido. Contacta al administrador.'
            ), 404

        pedido_id, estado_actual = r

        if estado_actual == 'Entregado':
            return render_template_string(PAGINA_CONFIRMACION,
                icono='✅',
                titulo='Pedido ya entregado',
                pedido_id=pedido_id,
                estado_clase='estado-entregado',
                estado_texto='Entregado',
                mostrar_boton=False,
                mensaje_final='Este pedido ya fue marcado como entregado anteriormente.'
            )

        if estado_actual != 'En camino':
            return render_template_string(PAGINA_CONFIRMACION,
                icono='⚠️',
                titulo='Estado no válido para confirmación',
                pedido_id=pedido_id,
                estado_clase='estado-error',
                estado_texto=estado_actual,
                mostrar_boton=False,
                mensaje_final=f'El pedido está en estado "{estado_actual}" y no puede confirmarse la entrega desde aquí.'
            )

        return render_template_string(PAGINA_CONFIRMACION,
            icono='🚚',
            titulo='Confirmar entrega',
            pedido_id=pedido_id,
            estado_clase='estado-camino',
            estado_texto='En camino',
            mostrar_boton=True,
            mensaje_final=None
        )

    except Exception as e:
        log.error(f"Error en confirmarEntrega: {e}", exc_info=True)
        return render_template_string(PAGINA_CONFIRMACION,
            icono='❌',
            titulo='Error del servidor',
            pedido_id='---',
            estado_clase='estado-error',
            estado_texto='Error interno',
            mostrar_boton=False,
            mensaje_final=f'Error interno: {str(e)}'
        ), 500


@safe_controller
def cnsiguienteidpedido():
    """Retorna el siguiente ID disponible para un nuevo pedido."""
    next_id = generarIdSiguiente("t_pedido", "ped_id", "PED", 3)
    return jsonify({"next_id": next_id}), 200
