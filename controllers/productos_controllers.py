from flask import jsonify, request, current_app
from services.productos_service import listarProductos, registrarProductos, editarProductos, eliminarProductos
from utils.validators import validar_campos_texto
from utils.error_handler import safe_controller

@safe_controller
def cnListarProductos():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    # Pasar filtros adicionales desde request.args
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarProductos(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnRegistrarProductos():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["id", "nombre", "categoria", "descripcion", "precio", "cantidad_disponible", "proveedor_id"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    # Validar campos no vacíos
    for campo in ["id", "nombre", "categoria", "descripcion"]:
        if str(data[campo]).strip() == "":
            return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

    PRECIO_MAXIMO = 999999.99
    CANTIDAD_MAXIMA = 999999

    # Validar precio positivo con tope
    try:
        precio = float(data["precio"])
        if precio <= 0:
            return jsonify({"mensaje": "El precio debe ser mayor a 0"}), 400
        if precio > PRECIO_MAXIMO:
            return jsonify({"mensaje": f"El precio no puede ser mayor a {PRECIO_MAXIMO:,.2f}"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "El precio debe ser un número válido"}), 400

    # Validar cantidad con tope
    try:
        cantidad = int(data["cantidad_disponible"])
        if cantidad < 0:
            return jsonify({"mensaje": "La cantidad disponible no puede ser negativa"}), 400
        if cantidad > CANTIDAD_MAXIMA:
            return jsonify({"mensaje": f"La cantidad disponible no puede ser mayor a {CANTIDAD_MAXIMA:,}"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "La cantidad disponible debe ser un número entero"}), 400

    # Validar stock mínimo con tope
    stock_min = 0
    if "stock_minimo" in data and data["stock_minimo"] is not None:
        try:
            stock_min = int(data["stock_minimo"])
            if stock_min < 0:
                return jsonify({"mensaje": "El stock mínimo no puede ser negativo"}), 400
            if stock_min > CANTIDAD_MAXIMA:
                return jsonify({"mensaje": f"El stock mínimo no puede ser mayor a {CANTIDAD_MAXIMA:,}"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El stock mínimo debe ser un número entero"}), 400

    # Validar que stock mínimo no supere al stock disponible
    if stock_min > cantidad:
        return jsonify({"mensaje": "El stock mínimo no puede superar al stock disponible"}), 400

    # Validar longitud de campos de texto
    errores = validar_campos_texto(data, "nombre", "categoria", "descripcion")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    # Validar estado
    estados_validos = ["Activo", "Descontinuado", "Suspendido"]
    if data.get("estado") and data["estado"] not in estados_validos:
        return jsonify({"mensaje": f"Estado inválido. Valores permitidos: {estados_validos}"}), 400

    # Validar duplicado por ID
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT pro_id FROM t_producto WHERE pro_id = %s", (data["id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un producto con el ID {data['id']}"}), 409

    # Validar que el proveedor exista
    c.execute("SELECT prov_id FROM t_proveedor WHERE prov_id = %s", (data["proveedor_id"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un proveedor con el ID {data['proveedor_id']}"}), 404
    c.close()

    resultado = registrarProductos(data)
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

    # Validar longitud de campos de texto editables
    errores = validar_campos_texto(data, "nombre", "categoria", "descripcion")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    PRECIO_MAXIMO = 999999.99
    CANTIDAD_MAXIMA = 999999

    if "precio" in data and data["precio"] is not None:
        try:
            precio = float(data["precio"])
            if precio <= 0:
                return jsonify({"mensaje": "El precio debe ser mayor a 0"}), 400
            if precio > PRECIO_MAXIMO:
                return jsonify({"mensaje": f"El precio no puede ser mayor a {PRECIO_MAXIMO:,.2f}"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El precio debe ser un número válido"}), 400

    if "cantidad_disponible" in data and data["cantidad_disponible"] is not None:
        try:
            cantidad = int(data["cantidad_disponible"])
            if cantidad < 0:
                return jsonify({"mensaje": "La cantidad no puede ser negativa"}), 400
            if cantidad > CANTIDAD_MAXIMA:
                return jsonify({"mensaje": f"La cantidad disponible no puede ser mayor a {CANTIDAD_MAXIMA:,}"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "La cantidad debe ser un número entero"}), 400

    stock_min = None
    if "stock_minimo" in data and data["stock_minimo"] is not None:
        try:
            stock_min = int(data["stock_minimo"])
            if stock_min < 0:
                return jsonify({"mensaje": "El stock mínimo no puede ser negativo"}), 400
            if stock_min > CANTIDAD_MAXIMA:
                return jsonify({"mensaje": f"El stock mínimo no puede ser mayor a {CANTIDAD_MAXIMA:,}"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El stock mínimo debe ser un número entero"}), 400

    # Validar que stock mínimo no supere al stock (si ambos se envían en la edición)
    cant_actualizada = data.get("cantidad_disponible")
    if stock_min is not None and cant_actualizada is not None:
        try:
            if stock_min > int(cant_actualizada):
                return jsonify({"mensaje": "El stock mínimo no puede superar al stock disponible"}), 400
        except (ValueError, TypeError):
            pass

    resultado = editarProductos(data["id"], data)
    return jsonify(resultado), 200
