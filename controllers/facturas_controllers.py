from flask import jsonify, request, current_app
from services.facturas_service import listarFacturas, registrarFacturas, editarFacturas, eliminarFacturas, buscarFacturas
from utils.validators import validar_campos_texto, contiene_emoji, validar_nombre_apellido
from utils.error_handler import safe_controller

@safe_controller
def cnListarFacturas():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarFacturas(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnRegistrarFacturas():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["id", "fecha_emision", "email_enviado", "forma_pago", "total", "usuario_id"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    # Validar longitud de campos de texto
    errores = validar_campos_texto(data, "forma_pago", "cuenta_bancaria")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    # Rechazar emojis en campos de texto
    for campo in ["forma_pago", "cuenta_bancaria"]:
        if data.get(campo) and contiene_emoji(str(data[campo])):
            return jsonify({"mensaje": f"El campo {campo} no puede contener emojis"}), 400

    # Validar que forma_pago solo contenga caracteres válidos (letras, números, espacios, -)
    if data.get("forma_pago"):
        import re
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s\-]+$', str(data["forma_pago"])):
            return jsonify({"mensaje": "La forma de pago solo puede contener letras, números, espacios y guiones"}), 400

    # Validar cuenta bancaria (solo bancos colombianos permitidos)
    BANCOS_PERMITIDOS = [
        "Bancolombia", "Davivienda", "Banco de Bogotá", "BBVA Colombia",
        "Banco de Occidente", "Banco Popular", "Banco Agrario", "Banco Caja Social",
        "Banco Falabella", "Scotiabank Colpatria", "Itaú Colombia", "Banco Pichincha",
        "Bancamía", "Bancoomeva", "AV Villas", "Nequi", "Daviplata", "Movii", "Dale"
    ]
    if data.get("cuenta_bancaria") and data["cuenta_bancaria"] not in BANCOS_PERMITIDOS:
        return jsonify({"mensaje": "Cuenta bancaria no válida. Seleccione una de la lista."}), 400

    # Validar email_enviado (0 o 1)
    if data["email_enviado"] not in [0, 1]:
        return jsonify({"mensaje": "email_enviado debe ser 0 o 1"}), 400

    # Validar estado
    estados_validos = ["Vigente", "Anulada"]
    if data.get("estado") and data["estado"] not in estados_validos:
        return jsonify({"mensaje": f"Estado inválido. Valores permitidos: {estados_validos}"}), 400

    # Validar total positivo
    try:
        total = float(data["total"])
        if total <= 0:
            return jsonify({"mensaje": "El total debe ser mayor a 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "El total debe ser un número válido"}), 400

    # Validar duplicado (fac_id = ped_id)
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT fac_id FROM t_factura WHERE fac_id = %s", (data["id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe una factura con el ID {data['id']}"}), 409

    # Validar que el pedido exista (fac_id referencia a ped_id)
    c.execute("SELECT ped_id FROM t_pedido WHERE ped_id = %s", (data["id"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un pedido con el ID {data['id']}. La factura debe referenciar un pedido existente"}), 404

    # Validar que el usuario exista
    c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (data["usuario_id"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un usuario con el ID {data['usuario_id']}"}), 404

    # Obtener el cliente asociado al pedido si no se envía cli_id_fk
    cli_id_fk = data.get('cli_id_fk')
    if not cli_id_fk:
        c.execute("SELECT ped_cli_id_fk FROM t_pedido WHERE ped_id = %s", (data["id"],))
        row = c.fetchone()
        if row:
            cli_id_fk = row[0]
    if cli_id_fk:
        c.execute("SELECT cli_id FROM t_cliente WHERE cli_id = %s", (cli_id_fk,))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un cliente con el ID {cli_id_fk}"}), 404
    c.close()

    data['cli_id_fk'] = cli_id_fk
    resultado = registrarFacturas(data)
    return jsonify(resultado), 201

@safe_controller
def cnEditarFacturas(fac_id):
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    # Obtener el cliente asociado al pedido si no se envía cli_id_fk
    cli_id_fk = data.get('cli_id_fk')
    if not cli_id_fk:
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT ped_cli_id_fk FROM t_pedido WHERE ped_id = %s", (fac_id,))
        row = c.fetchone()
        if row:
            cli_id_fk = row[0]
        c.close()
    if cli_id_fk:
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT cli_id FROM t_cliente WHERE cli_id = %s", (cli_id_fk,))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un cliente con el ID {cli_id_fk}"}), 404
        c.close()

    data['cli_id_fk'] = cli_id_fk
    resultado = editarFacturas(fac_id, data)
    return jsonify(resultado), 200

@safe_controller
def cnEliminarFacturas(fac_id):
    try:
        resultado = eliminarFacturas(fac_id)
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"mensaje": str(e)}), 409

@safe_controller
def cnBuscarFacturas(fac_id):
    dato = buscarFacturas(fac_id)
    if dato:
        return jsonify(dato), 200
    return jsonify({"mensaje": "Factura no encontrada"}), 404
