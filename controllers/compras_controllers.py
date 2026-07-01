from datetime import date
from flask import jsonify, request, current_app
from services.compras_service import listarCompras, registrarCompras, buscarCompras, editarCompras, eliminarCompras
from utils.validators import validar_campos_texto
from utils.error_handler import safe_controller

@safe_controller
def cnlistadocompras():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarCompras(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnregistrarcompras():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["com_id", "com_fecha", "com_prov_id_fk", "com_usu_id_fk", "com_total", "com_estado", "com_observacion"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    for campo in ["com_id", "com_fecha", "com_prov_id_fk", "com_usu_id_fk"]:
        if str(data[campo]).strip() == "":
            return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

    # Validar fecha (no fechas futuras ni absurdas)
    try:
        fecha_str = data["com_fecha"]
        if isinstance(fecha_str, str):
            año, mes, dia = map(int, fecha_str.split("-"))
            fecha_obj = date(año, mes, dia)
            if año < 2020:
                return jsonify({"mensaje": "La fecha de la compra no es válida (año muy antiguo)"}), 400
            if fecha_obj < date.today():
                return jsonify({"mensaje": "La fecha de la compra no puede ser anterior a hoy"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "El formato de la fecha no es válido (use YYYY-MM-DD)"}), 400

    # Validar longitud de campos de texto
    errores = validar_campos_texto(data, "com_observacion", "com_comprobante_tipo")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    # En POST (crear) no se permite "Cancelada" - solo al editar (PUT)
    estados_validos = ["Pendiente", "Recibida"]
    if data["com_estado"] not in estados_validos:
        return jsonify({"mensaje": f"Estado inválido al crear. Valores permitidos: {estados_validos}"}), 400

    TOTAL_MAXIMO = 9999999.99
    try:
        total = float(data["com_total"])
        if total <= 0:
            return jsonify({"mensaje": "El total debe ser mayor a 0"}), 400
        if total > TOTAL_MAXIMO:
            return jsonify({"mensaje": f"El total no puede ser mayor a {TOTAL_MAXIMO:,.2f}"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "El total debe ser un número válido"}), 400

    c = current_app.mysql.connection.cursor()
    c.execute("SELECT com_id FROM t_compra WHERE com_id = %s", (data["com_id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe una compra con el ID {data['com_id']}"}), 409

    c.execute("SELECT prov_id FROM t_proveedor WHERE prov_id = %s", (data["com_prov_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un proveedor con el ID {data['com_prov_id_fk']}"}), 404

    c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (data["com_usu_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un usuario con el ID {data['com_usu_id_fk']}"}), 404
    c.close()

    resultado = registrarCompras(
        data["com_id"], data["com_fecha"], data["com_prov_id_fk"],
        data["com_usu_id_fk"], data["com_total"], data["com_estado"], data["com_observacion"],
        data.get("com_comprobante"), data.get("com_comprobante_tipo")
    )
    return jsonify({"mensaje": "Compra registrada correctamente", "datos": resultado}), 201

@safe_controller
def cnbuscarcompras(COM_ID):
    resultado = buscarCompras(COM_ID)
    if resultado is None:
        return jsonify({"mensaje": f"No se encontró la compra con ID {COM_ID}"}), 404
    return jsonify(resultado), 200

@safe_controller
def cneditarcompras(COM_ID):
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    # Validar fecha (no fechas absurdas — en edición se permiten fechas pasadas)
    if data.get("com_fecha"):
        try:
            fecha_str = data["com_fecha"]
            if isinstance(fecha_str, str):
                año, mes, dia = map(int, fecha_str.split("-"))
                fecha_obj = date(año, mes, dia)
                if año < 2020:
                    return jsonify({"mensaje": "La fecha de la compra no es válida (año muy antiguo)"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El formato de la fecha no es válido (use YYYY-MM-DD)"}), 400

    if data.get("com_estado"):
        estados_validos = ["Pendiente", "Recibida", "Cancelada"]
        if data["com_estado"] not in estados_validos:
            return jsonify({"mensaje": f"Estado inválido. Valores permitidos: {estados_validos}"}), 400

    # Validar que no se cambie el proveedor si la compra ya tiene detalles
    if data.get("com_prov_id_fk"):
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT COUNT(*) FROM t_detalle_compra WHERE dco_com_id_fk = %s", (COM_ID,))
        tiene_detalles = c.fetchone()[0] > 0
        c.close()
        if tiene_detalles:
            # Obtener el proveedor actual para comparar
            compra_actual = buscarCompras(COM_ID)
            proveedor_actual = compra_actual.get("comp_prov_id_fk") if compra_actual else None
            if str(data["com_prov_id_fk"]) != str(proveedor_actual):
                return jsonify({"mensaje": "No se puede cambiar el proveedor porque la compra ya tiene productos asociados"}), 400

    TOTAL_MAXIMO = 9999999.99
    if data.get("com_total"):
        try:
            total = float(data["com_total"])
            if total <= 0:
                return jsonify({"mensaje": "El total debe ser mayor a 0"}), 400
            if total > TOTAL_MAXIMO:
                return jsonify({"mensaje": f"El total no puede ser mayor a {TOTAL_MAXIMO:,.2f}"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El total debe ser un número válido"}), 400

    if data.get("com_prov_id_fk"):
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT prov_id FROM t_proveedor WHERE prov_id = %s", (data["com_prov_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un proveedor con el ID {data['com_prov_id_fk']}"}), 404
        c.close()

    compra = buscarCompras(COM_ID)
    if compra is None:
        return jsonify({"mensaje": f"No se encontró la compra con ID {COM_ID}"}), 404

    compra_data = {
        "com_fecha": data.get("com_fecha", compra.get("comp_fecha")),
        "com_prov_id_fk": data.get("com_prov_id_fk", compra.get("comp_prov_id_fk")),
        "com_usu_id_fk": data.get("com_usu_id_fk", compra.get("comp_usu_id_fk")),
        "com_total": data.get("com_total", compra.get("comp_total")),
        "com_estado": data.get("com_estado", compra.get("comp_estado")),
        "com_observacion": data.get("com_observacion", compra.get("comp_observacion")),
    }

    if "com_comprobante" in data:
        compra_data["com_comprobante"] = data["com_comprobante"]
        compra_data["com_comprobante_tipo"] = data.get("com_comprobante_tipo")

    resultado = editarCompras(COM_ID, compra_data)
    return jsonify(resultado), 200

@safe_controller
def cneliminarcompras(COM_ID):
    compra = buscarCompras(COM_ID)
    if compra is None:
        return jsonify({"mensaje": f"No se encontró la compra con ID {COM_ID}"}), 404
    try:
        resultado = eliminarCompras(COM_ID)
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"mensaje": str(e)}), 409
