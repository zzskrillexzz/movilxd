from flask import jsonify, request, current_app
from services.productos_service import listarProductos, registrarProductos, editarProductos, eliminarProductos
from utils.validators import validar_campos_texto
from utils.error_handler import safe_controller

PRECIO_MINIMO = 100
PRECIO_MAXIMO = 999999.99
ESTADOS_VALIDOS = ["Activo", "Descontinuado", "Suspendido"]

def _validar_precio(precio):
    try:
        p = float(precio)
        if p < PRECIO_MINIMO:
            return f"El precio no puede ser menor a ${PRECIO_MINIMO:,.0f} COP"
        if p > PRECIO_MAXIMO:
            return f"El precio no puede ser mayor a {PRECIO_MAXIMO:,.2f}"
        return None
    except (ValueError, TypeError):
        return "El precio debe ser un número válido"

@safe_controller
def cnListarProductos():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarProductos(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnRegistrarProductos():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["id", "nombre", "categoria", "descripcion", "precio"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    for campo in ["id", "nombre", "categoria", "descripcion"]:
        if str(data[campo]).strip() == "":
            return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

    err_precio = _validar_precio(data.get("precio"))
    if err_precio:
        return jsonify({"mensaje": err_precio}), 400

    errores = validar_campos_texto(data, "nombre", "categoria", "descripcion")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    if data.get("estado") and data["estado"] not in ESTADOS_VALIDOS:
        return jsonify({"mensaje": f"Estado inválido. Valores permitidos: {ESTADOS_VALIDOS}"}), 400

    c = current_app.mysql.connection.cursor()
    c.execute("SELECT pro_id FROM t_producto WHERE pro_id = %s", (data["id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un producto con el ID {data['id']}"}), 409
    c.close()

    proveedor_id = data.get("proveedor_id")
    if proveedor_id:
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT prov_id FROM t_proveedor WHERE prov_id = %s", (proveedor_id,))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un proveedor con el ID {proveedor_id}"}), 404
        c.close()

    resultado = registrarProductos(data, proveedor_id=proveedor_id)
    return jsonify(resultado), 201

@safe_controller
def cnEliminarProductos(id):
    fuerza = request.args.get('force', 'false').lower() == 'true'
    resultado, codigo = eliminarProductos(id, fuerza=fuerza)
    return jsonify(resultado), codigo


@safe_controller
def cnEditarProductos():
    data = request.get_json()
    if not data or "id" not in data:
        return jsonify({"mensaje": "ID del producto requerido"}), 400

    errores = validar_campos_texto(data, "nombre", "categoria", "descripcion")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    if "precio" in data and data["precio"] is not None:
        err_precio = _validar_precio(data["precio"])
        if err_precio:
            return jsonify({"mensaje": err_precio}), 400

    resultado = editarProductos(data["id"], data)
    return jsonify(resultado), 200
