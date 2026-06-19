import re
from flask import jsonify, request, current_app
from services.clientes_service import listarClientes, registrarClientes, editarClientes, eliminarClientes, buscarClientes
from utils.validators import validar_campos_texto, validar_nombre_apellido
from utils.error_handler import safe_controller

# ── Patrón para teléfono: solo dígitos, espacios, +, -, ( ) ──
PATRON_TELEFONO = re.compile(r'^[\d\s\+\-\(\)]+$')


def _validar_telefono(telefono):
    """Valida que el teléfono solo contenga caracteres permitidos. Retorna None si es válido."""
    if not telefono or str(telefono).strip() == "":
        return None  # campo opcional, vacío es válido
    if not PATRON_TELEFONO.match(str(telefono)):
        return "El teléfono solo puede contener dígitos, espacios, +, -, ( y )"
    return None

@safe_controller
def cnlistadoclientes():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    return jsonify(listarClientes(page=page, limit=limit, q=q, order_by=order_by, **filtros)), 200

@safe_controller
def cnregistrarclientes():
    data = request.get_json()
    requerido = ["cli_id", "cli_tipo_documento", "cli_nombre", "cli_apellido", "cli_correo"]
    
    if not data or any(x not in data for x in requerido):
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

    # Validar que cli_id sea un entero positivo
    try:
        cli_id = int(data["cli_id"])
        if cli_id <= 0:
            return jsonify({"mensaje": "El ID del cliente debe ser un número positivo"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "El ID del cliente debe ser un número entero"}), 400

    # Validar ID duplicado
    if buscarClientes(data["cli_id"]):
        return jsonify({"mensaje": f"El cliente con ID {data['cli_id']} ya existe"}), 409

    # Validar longitud de campos de texto
    errores = validar_campos_texto(
        data, "cli_tipo_documento", "cli_nombre", "cli_apellido",
        "cli_correo", "cli_telefono", "cli_direccion"
    )
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    # Validar que nombres no tengan caracteres especiales
    err_nom = validar_nombre_apellido(data.get("cli_nombre"), "nombre")
    if err_nom:
        return jsonify({"mensaje": err_nom}), 400
    err_ape = validar_nombre_apellido(data.get("cli_apellido"), "apellido")
    if err_ape:
        return jsonify({"mensaje": err_ape}), 400

    # Validar formato del teléfono
    err_tel = _validar_telefono(data.get("cli_telefono"))
    if err_tel:
        return jsonify({"mensaje": err_tel}), 400

    # Validar Correo duplicado
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT cli_id FROM t_cliente WHERE cli_correo = %s", (data["cli_correo"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": "El correo ya está registrado"}), 409
    c.close()

    resultado = registrarClientes(
        data["cli_id"], data["cli_tipo_documento"], data["cli_nombre"],
        data["cli_apellido"], data.get("cli_telefono"), data.get("cli_direccion"), data["cli_correo"]
    )
    return jsonify({"mensaje": "Cliente registrado", "datos": resultado}), 201

@safe_controller
def cneditarclientes():
    data = request.get_json()
    if not data or "cli_id" not in data:
        return jsonify({"mensaje": "ID de cliente requerido"}), 400

    # Validar que cli_id sea un entero positivo
    try:
        cli_id = int(data["cli_id"])
        if cli_id <= 0:
            return jsonify({"mensaje": "El ID del cliente debe ser un número positivo"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "El ID del cliente debe ser un número entero"}), 400

    # Validar longitud de campos de texto
    errores = validar_campos_texto(
        data, "cli_tipo_documento", "cli_nombre", "cli_apellido",
        "cli_correo", "cli_telefono", "cli_direccion"
    )
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    # Validar que nombres no tengan caracteres especiales
    err_nom = validar_nombre_apellido(data.get("cli_nombre"), "nombre")
    if err_nom:
        return jsonify({"mensaje": err_nom}), 400
    err_ape = validar_nombre_apellido(data.get("cli_apellido"), "apellido")
    if err_ape:
        return jsonify({"mensaje": err_ape}), 400

    # Validar formato del teléfono
    err_tel = _validar_telefono(data.get("cli_telefono"))
    if err_tel:
        return jsonify({"mensaje": err_tel}), 400

    # Validar que el correo no lo tenga otro cliente
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT cli_id FROM t_cliente WHERE cli_correo = %s AND cli_id != %s", (data["cli_correo"], data["cli_id"]))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": "El correo ya pertenece a otro cliente"}), 409
    c.close()

    resultado = editarClientes(
        data["cli_id"], data["cli_tipo_documento"], data["cli_nombre"],
        data["cli_apellido"], data.get("cli_telefono"), data.get("cli_direccion"), data["cli_correo"]
    )
    return jsonify({"mensaje": "Cliente actualizado", "datos": resultado}), 200

@safe_controller
def cneliminarclientes(cli_id):
    if not buscarClientes(cli_id):
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    return jsonify(eliminarClientes(cli_id)), 200

@safe_controller
def cnbuscarclientes():
    cli_id = request.args.get("cli_id")
    resultado = buscarClientes(cli_id)
    if resultado:
        return jsonify(resultado), 200
    return jsonify({"mensaje": "Cliente no encontrado"}), 404
