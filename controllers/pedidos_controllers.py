from flask import jsonify, request, current_app, render_template_string
from services.pedidos_service import (
    listarPedidos, registrarPedidos,
    editarPedidos, eliminarPedidos, buscarPedido, verificarPago,
    subirComprobante, avanzarEstado, enviarFacturaEmail,
    confirmarEntregaPorToken
)
from utils.id_generator import generarIdSiguiente
from services.clientes_service import buscarClientes
from services.notificaciones_service import enviar_email, enviar_whatsapp, generar_mensaje_pedido_listo

def cnlistadopedidos():
    try:
        x = listarPedidos()
        return jsonify(x), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

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

        # Validar método de pago
        metodos_validos = ["Efectivo", "Tarjeta", "Transferencia", "Nequi", "Daviplata"]
        if data["ped_metodo_pago"] not in metodos_validos:
            return jsonify({"mensaje": f"Método de pago inválido. Valores permitidos: {metodos_validos}"}), 400

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

        # Validar duplicado
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT ped_id FROM t_pedido WHERE ped_id = %s", (ped_id,))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": f"Ya existe un pedido con el ID {ped_id}"}), 409

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

        resultado = registrarPedidos(
            ped_id, data["ped_fecha"], data["ped_metodo_pago"],
            data["ped_estado_entrega"], data["ped_total"], data["ped_cli_id_fk"],
            data.get("ped_cuenta_bancaria"),
            data.get("ped_comprobante"),
            data.get("ped_comprobante_tipo"),
            fk_usuario
        )
        return jsonify({"mensaje": "Pedido realizado correctamente", "datos": resultado}), 201

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnbuscarpedido(id):
    try:
        pedido = buscarPedido(id)
        if not pedido:
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404
        return jsonify(pedido), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnsubircomprobante(id):
    try:
        pedido = buscarPedido(id)
        if not pedido:
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        data = request.get_json()
        if not data or not data.get("ped_comprobante") or not data.get("ped_comprobante_tipo"):
            return jsonify({"mensaje": "Debe enviar ped_comprobante (base64) y ped_comprobante_tipo"}), 400

        resultado = subirComprobante(
            id, data["ped_comprobante"], data["ped_comprobante_tipo"]
        )
        if resultado:
            return jsonify({"mensaje": "Comprobante subido correctamente", "datos": resultado}), 200
        return jsonify({"mensaje": "No se pudo actualizar el comprobante"}), 500

    except Exception as e:
        import traceback
        print(traceback.format_exc())
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
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnenviarfactura(id):
    try:
        pedido = buscarPedido(id)
        if not pedido:
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        resultado = enviarFacturaEmail(id)
        if resultado.get('ok'):
            return jsonify(resultado), 200
        return jsonify(resultado), 400

    except Exception as e:
        import traceback
        print(traceback.format_exc())
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

        metodos_validos = ["Efectivo", "Tarjeta", "Transferencia", "Nequi", "Daviplata"]
        if data["ped_metodo_pago"] not in metodos_validos:
            return jsonify({"mensaje": f"Método de pago inválido. Valores permitidos: {metodos_validos}"}), 400

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
        import traceback
        print(traceback.format_exc())
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
            return jsonify({"mensaje": f"Pago del pedido {id} marcado como {estado}", "ped_estado_pago": estado}), 200
        return jsonify({"mensaje": "No se pudo actualizar el estado del pago"}), 500

    except Exception as e:
        import traceback
        print(traceback.format_exc())
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
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def cneliminarpedidos(id):
    try:
        if not buscarPedido(id):
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        # Verificar si el pedido tiene detalles asociados
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT det_id FROM t_detalle_pedido WHERE det_ped_id_fk=%s LIMIT 1", (id,))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": "No se puede eliminar: el pedido tiene detalles asociados"}), 409
        c.close()

        if eliminarPedidos(id):
            return jsonify({"mensaje": f"Pedido {id} eliminado correctamente"}), 200
        return jsonify({"mensaje": "No se pudo eliminar el pedido"}), 500

    except Exception as e:
        import traceback
        print(traceback.format_exc())
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
        import traceback
        print(traceback.format_exc())
        return render_template_string(PAGINA_CONFIRMACION,
            icono='❌',
            titulo='Error del servidor',
            pedido_id='---',
            estado_clase='estado-error',
            estado_texto='Error interno',
            mostrar_boton=False,
            mensaje_final=f'Error interno: {str(e)}'
        ), 500
