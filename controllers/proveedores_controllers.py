from flask import jsonify, request, current_app
from services.proveedores_service import listarProveedores, registrarProveedores, buscarProveedores, editarProveedores, eliminarProveedores
import re
from utils.validators import validar_campos_texto
from utils.error_handler import safe_controller

# ── Patrón básico de email ──
_EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

@safe_controller
def cnlistadoproveedores():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarProveedores(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnregistrarproveedores():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["nit", "nombre", "tipo", "contacto", "direccion", "email"]
    faltantes = [x for x in requerido if x not in data or str(data[x]).strip() == ""]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos o están vacíos: {faltantes}"}), 400

    # Auto-generar ID siempre (el backend es la autoridad, ignora lo que envíe el frontend)
    from utils.id_generator import generarIdSiguiente
    data['id'] = generarIdSiguiente('t_proveedor', 'prov_id', 'PROV', 3)

    # Validar longitud de campos de texto
    errores = validar_campos_texto(data, "nit", "nombre", "tipo", "contacto", "direccion", "email")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    # Validar tipo
    tipos_validos = ["Laboratorio", "Distribuidor", "Importador"]
    if data["tipo"] not in tipos_validos:
        return jsonify({"mensaje": f"Tipo inválido. Valores permitidos: {tipos_validos}"}), 400

    # Validar formato email
    if not _EMAIL_RE.match(data.get("email", "")):
        return jsonify({"mensaje": "El formato del email no es válido"}), 400

    # Validar duplicado por ID
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT prov_id FROM t_proveedor WHERE prov_id = %s", (data["id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un proveedor con el ID {data['id']}"}), 409

    # Validar NIT duplicado
    c.execute("SELECT prov_id FROM t_proveedor WHERE prov_nit = %s", (data["nit"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un proveedor con el NIT {data['nit']}"}), 409
    c.close()

    resultado = registrarProveedores(data)
    resultado['prov_id'] = data['id']
    return jsonify(resultado), 201


@safe_controller
def cnbuscarproveedores():
    prov_id = request.args.get('prov_id')
    if not prov_id:
        return jsonify({"mensaje": "Debe enviar el parámetro prov_id"}), 400
    resultado = buscarProveedores(prov_id)
    if resultado is None:
        return jsonify({"mensaje": f"No se encontró el proveedor con ID {prov_id}"}), 404
    return jsonify(resultado), 200


@safe_controller
def cneditarproveedores():
    data = request.get_json()
    if not data or not data.get('id'):
        return jsonify({"mensaje": "Debe enviar el ID del proveedor"}), 400

    prov_id = data['id']
    if not buscarProveedores(prov_id):
        return jsonify({"mensaje": f"No existe un proveedor con el ID {prov_id}"}), 404

    requerido = ["nit", "nombre", "tipo", "contacto", "direccion", "email"]
    faltantes = [x for x in requerido if x not in data or str(data[x]).strip() == ""]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos o están vacíos: {faltantes}"}), 400

    # Validar longitud de campos de texto
    errores = validar_campos_texto(data, "nit", "nombre", "tipo", "contacto", "direccion", "email")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    # Validar tipo
    tipos_validos = ["Laboratorio", "Distribuidor", "Importador"]
    if data["tipo"] not in tipos_validos:
        return jsonify({"mensaje": f"Tipo inválido. Valores permitidos: {tipos_validos}"}), 400

    # Validar formato email
    if not _EMAIL_RE.match(data.get("email", "")):
        return jsonify({"mensaje": "El formato del email no es válido"}), 400

    # Validar NIT duplicado (si cambió)
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT prov_id FROM t_proveedor WHERE prov_nit = %s AND prov_id != %s", (data["nit"], prov_id))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe otro proveedor con el NIT {data['nit']}"}), 409
    c.close()

    resultado = editarProveedores(prov_id, data)
    return jsonify(resultado), 200


@safe_controller
def cneliminarproveedores(prov_id):
    if not buscarProveedores(prov_id):
        return jsonify({"mensaje": f"No existe un proveedor con el ID {prov_id}"}), 404
    resultado = eliminarProveedores(prov_id)
    return jsonify(resultado), 200
