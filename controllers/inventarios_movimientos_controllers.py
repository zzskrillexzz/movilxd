from flask import jsonify, request, current_app
from services.inventarios_movimientos_service import listarInventariosMovimientos, registrarInventariosMovimientos
from utils.validators import validar_campos_texto
from utils.error_handler import safe_controller

@safe_controller
def cnlistadoinventariosmovimientos():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)

    # Mapear nombres de parámetros HTTP → columnas internas del SearchBuilder
    MAPEO = {
        'tipo': 'inm_tipo_movimiento',
        'fecha_desde': 'inm_fecha_from',
        'fecha_hasta': 'inm_fecha_to',
    }
    filtros = {}
    for k, v in request.args.items():
        if k in ('page', 'limit', 'q', 'order_by'):
            continue
        columna = MAPEO.get(k, k)
        filtros[columna] = v

    datos = listarInventariosMovimientos(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnregistrarinventariosmovimientos():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["inm_id", "inm_tipo_movimiento", "inm_pro_id_fk", "inm_cantidad", "inm_fecha", "inm_motivo", "inm_usu_id_fk"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    # Validar longitud del motivo
    msg = validar_campos_texto(data, "inm_motivo")
    if msg:
        return jsonify({"mensaje": " | ".join(msg)}), 400

    # Validar tipo movimiento
    tipos_validos = ["Entrada", "Salida", "Ajuste"]
    if data["inm_tipo_movimiento"] not in tipos_validos:
        return jsonify({"mensaje": f"Tipo de movimiento inválido. Valores permitidos: {tipos_validos}"}), 400

    # Validar cantidad positiva
    try:
        cantidad = int(data["inm_cantidad"])
        if cantidad <= 0:
            return jsonify({"mensaje": "La cantidad debe ser mayor a 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "La cantidad debe ser un número entero"}), 400

    # Validar duplicado
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT inm_id FROM t_inventario_movimiento WHERE inm_id = %s", (data["inm_id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un movimiento con el ID {data['inm_id']}"}), 409

    # Validar que el producto exista
    c.execute("SELECT pro_id FROM t_producto WHERE pro_id = %s", (data["inm_pro_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un producto con el ID {data['inm_pro_id_fk']}"}), 404

    # Validar que el usuario exista
    c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (data["inm_usu_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un usuario con el ID {data['inm_usu_id_fk']}"}), 404

    # Validar lote si se envía
    lote_id = data.get("inm_lot_id_fk")
    if lote_id:
        c.execute("SELECT lot_id FROM t_lote WHERE lot_id = %s", (lote_id,))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un lote con el ID {lote_id}"}), 404
        c.close()

    resultado = registrarInventariosMovimientos(
        data["inm_id"], data["inm_tipo_movimiento"], data["inm_pro_id_fk"],
        data["inm_cantidad"], data["inm_fecha"], data["inm_motivo"],
        data["inm_usu_id_fk"], lote_id
    )
    return jsonify({"mensaje": "Movimiento de inventario registrado correctamente", "datos": resultado}), 201
