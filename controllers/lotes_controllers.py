from datetime import datetime, timedelta, date
from flask import jsonify, request, current_app
from services.lotes_service import listarLotes, registrarLotes, editarLotes, eliminarLotes, activarLote
from utils.validators import validar_campos_texto
from utils.error_handler import safe_controller

# ── Constantes ──
VIDA_UTIL_MINIMA_DIAS = 14          # Mínimo de días entre fabricación y vencimiento
AÑOS_ATRAS_MAXIMO = 5               # Años máximos hacia atrás desde el año actual (dinámico)
AÑOS_ADELANTE_MAXIMO = 5            # Años máximos hacia adelante desde el año actual (dinámico)
VIDA_UTIL_MAXIMA_DIAS = 5 * 365     # Máximo ~5 años entre fabricación y vencimiento
CANTIDAD_MAXIMA = 1000              # Tope máximo para cantidades en lote


def _validar_fechas_lote(fecha_fabricacion, fecha_vencimiento, es_post=True):
    """
    Valida que las fechas del lote sean razonables:
    - Año >= año actual - AÑOS_ATRAS_MAXIMO y <= año actual + AÑOS_ADELANTE_MAXIMO
    - Fecha de vencimiento >= fecha de fabricación + VIDA_UTIL_MINIMA_DIAS
    - Fecha de vencimiento <= fecha de fabricación + VIDA_UTIL_MAXIMA_DIAS (~5 años)
    Los límites se recalculan cada vez (dinámicos, no estáticos).
    Retorna (None, None) si ok, o (mensaje_error_400, "mensaje") si hay error.
    """
    hoy = date.today()
    año_minimo = hoy.year - AÑOS_ATRAS_MAXIMO
    año_maximo = hoy.year + AÑOS_ADELANTE_MAXIMO

    try:
        if fecha_fabricacion:
            fab = datetime.strptime(fecha_fabricacion, "%Y-%m-%d").date()
            if fab.year < año_minimo or fab.year > año_maximo:
                return f"La fecha de fabricación debe estar entre {año_minimo} y {año_maximo}", 400
        else:
            fab = None
    except (ValueError, TypeError):
        return "La fecha de fabricación no tiene un formato válido (YYYY-MM-DD)", 400

    try:
        ven = datetime.strptime(fecha_vencimiento, "%Y-%m-%d").date()
        if ven.year < año_minimo or ven.year > año_maximo:
            return f"La fecha de vencimiento debe estar entre {año_minimo} y {año_maximo}", 400
    except (ValueError, TypeError):
        return "La fecha de vencimiento no tiene un formato válido (YYYY-MM-DD)", 400

    if fab and ven <= fab:
        return "La fecha de vencimiento debe ser posterior a la fecha de fabricación", 400

    if fab and (ven - fab).days < VIDA_UTIL_MINIMA_DIAS:
        return f"La fecha de vencimiento debe ser al menos {VIDA_UTIL_MINIMA_DIAS} días después de la fecha de fabricación", 400

    if fab and (ven - fab).days > VIDA_UTIL_MAXIMA_DIAS:
        return f"La fecha de vencimiento no puede ser más de {AÑOS_ADELANTE_MAXIMO} años después de la fecha de fabricación", 400

    return None, None


def _validar_cantidad_lote(cantidad_str, nombre_campo, permitir_cero=False):
    """Valida cantidad entera positiva con tope máximo."""
    try:
        cant = int(cantidad_str)
        if permitir_cero:
            if cant < 0:
                return f"La {nombre_campo} no puede ser negativa"
        else:
            if cant <= 0:
                return f"La {nombre_campo} debe ser mayor a 0"
        if cant > CANTIDAD_MAXIMA:
            return f"La {nombre_campo} no puede ser mayor a {CANTIDAD_MAXIMA:,}"
        return None
    except (ValueError, TypeError):
        return f"La {nombre_campo} debe ser un número entero"

@safe_controller
def cnlistadolotes():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarLotes(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnregistrarlotes():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["lot_id", "lot_numero", "lot_fecha_fabricacion", "lot_fecha_vencimiento", "lot_cantidad_inicial", "lot_cantidad_actual", "lot_pro_id_fk", "lot_prov_id_fk", "lot_estado"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    # Validar longitud del número de lote
    msg = validar_campos_texto(data, "lot_numero")
    if msg:
        return jsonify({"mensaje": " | ".join(msg)}), 400

    # Validar estado
    estados_validos = ["Activo", "Agotado", "Vencido", "Cuarentena", "Pendiente"]
    if data["lot_estado"] not in estados_validos:
        return jsonify({"mensaje": f"Estado inválido. Valores permitidos: {estados_validos}"}), 400

    # Validar fechas (rango de años y vida útil mínima)
    err_fechas, cod = _validar_fechas_lote(
        data.get("lot_fecha_fabricacion"),
        data["lot_fecha_vencimiento"]
    )
    if err_fechas:
        return jsonify({"mensaje": err_fechas}), cod

    # Validar cantidades (positivas + tope máximo)
    err_cant = _validar_cantidad_lote(data["lot_cantidad_inicial"], "cantidad inicial")
    if err_cant:
        return jsonify({"mensaje": err_cant}), 400

    err_cant_act = _validar_cantidad_lote(data["lot_cantidad_actual"], "cantidad actual", permitir_cero=True)
    if err_cant_act:
        return jsonify({"mensaje": err_cant_act}), 400

    try:
        if int(data["lot_cantidad_actual"]) > int(data["lot_cantidad_inicial"]):
            return jsonify({"mensaje": "La cantidad actual no puede ser mayor a la cantidad inicial"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "Las cantidades deben ser números enteros"}), 400

    # Validar duplicado
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT lot_id FROM t_lote WHERE lot_id = %s", (data["lot_id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un lote con el ID {data['lot_id']}"}), 409

    # Validar que el número de lote no esté duplicado
    c.execute("SELECT lot_id FROM t_lote WHERE lot_numero = %s AND lot_id != %s", (data.get("lot_numero", ""), data.get("lot_id", "")))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"El número de lote '{data.get('lot_numero')}' ya existe. Debe ser único."}), 409

    # Validar que el producto exista
    c.execute("SELECT pro_id FROM t_producto WHERE pro_id = %s", (data["lot_pro_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un producto con el ID {data['lot_pro_id_fk']}"}), 404

    # Validar que el proveedor exista
    c.execute("SELECT prov_id FROM t_proveedor WHERE prov_id = %s", (data["lot_prov_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un proveedor con el ID {data['lot_prov_id_fk']}"}), 404

    # Validar que el producto esté asociado al proveedor
    c.execute("SELECT ppp_prov_id_fk FROM t_proveedor_producto WHERE ppp_prov_id_fk = %s AND ppp_pro_id_fk = %s",
              (data["lot_prov_id_fk"], data["lot_pro_id_fk"]))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"El producto {data['lot_pro_id_fk']} no está asociado al proveedor {data['lot_prov_id_fk']}"}), 400
    c.close()

    resultado = registrarLotes(
        data["lot_id"], data["lot_numero"], data["lot_fecha_fabricacion"],
        data["lot_fecha_vencimiento"], data["lot_cantidad_inicial"], data["lot_cantidad_actual"],
        data["lot_pro_id_fk"], data["lot_prov_id_fk"], data["lot_estado"]
    )
    return jsonify({"mensaje": "Lote registrado correctamente", "datos": resultado}), 201

@safe_controller
def cnEliminarLotes(id):
    fuerza = request.args.get('force', 'false').lower() == 'true'
    resultado, codigo = eliminarLotes(id, fuerza=fuerza)
    return jsonify(resultado), codigo


@safe_controller
def cnEditarlotes():
    data = request.get_json()
    if not data or "lot_id" not in data:
        return jsonify({"mensaje": "ID del lote requerido"}), 400

    # Validar fechas si se envían (rango de años y vida útil mínima)
    if "lot_fecha_fabricacion" in data or "lot_fecha_vencimiento" in data:
        # Obtener valores actuales de la BD para comparar
        lote_actual = None
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT lot_fecha_fabricacion, lot_fecha_vencimiento FROM t_lote WHERE lot_id = %s", (data["lot_id"],))
        row = c.fetchone()
        c.close()
        if row:
            lote_actual = {"fab": str(row[0]) if row[0] else None, "ven": str(row[1]) if row[1] else None}

        fab = data.get("lot_fecha_fabricacion", lote_actual["fab"] if lote_actual else None)
        ven = data.get("lot_fecha_vencimiento", lote_actual["ven"] if lote_actual else None)
        err_fechas, cod = _validar_fechas_lote(fab, ven)
        if err_fechas:
            return jsonify({"mensaje": err_fechas}), cod

    # Validar cantidad inicial si se envía
    if "lot_cantidad_inicial" in data and data["lot_cantidad_inicial"] is not None:
        err_cant = _validar_cantidad_lote(data["lot_cantidad_inicial"], "cantidad inicial")
        if err_cant:
            return jsonify({"mensaje": err_cant}), 400

    # Validar cantidad actual si se envía
    if "lot_cantidad_actual" in data and data["lot_cantidad_actual"] is not None:
        err_cant = _validar_cantidad_lote(data["lot_cantidad_actual"], "cantidad actual", permitir_cero=True)
        if err_cant:
            return jsonify({"mensaje": err_cant}), 400

    # Validar relación producto-proveedor si ambos campos están presentes
    if "lot_pro_id_fk" in data and "lot_prov_id_fk" in data and data["lot_pro_id_fk"] and data["lot_prov_id_fk"]:
        c2 = current_app.mysql.connection.cursor()
        c2.execute("SELECT ppp_prov_id_fk FROM t_proveedor_producto WHERE ppp_prov_id_fk = %s AND ppp_pro_id_fk = %s",
                   (data["lot_prov_id_fk"], data["lot_pro_id_fk"]))
        if not c2.fetchone():
            c2.close()
            return jsonify({"mensaje": f"El producto {data['lot_pro_id_fk']} no está asociado al proveedor {data['lot_prov_id_fk']}"}), 400
        c2.close()

    resultado = editarLotes(data["lot_id"], data)
    return jsonify(resultado), 200


@safe_controller
def cnActivarlote(lot_id):
    resultado, codigo = activarLote(lot_id)
    return jsonify(resultado), codigo
