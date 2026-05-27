from flask import jsonify, request, current_app
from services.monitorias_service import (
    listarMonitoria, registrarMonitoria,
    editarMonitoria, eliminarMonitoria, buscarMonitoria
)
from utils.error_handler import safe_controller

@safe_controller
def cnlistarMonitoria():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)

    # Mapear nombres de parámetros HTTP → columnas internas del SearchBuilder
    MAPEO = {
        'tipo': 'mon_tipo',
        'fecha_desde': 'mon_fecha_from',
        'fecha_hasta': 'mon_fecha_to',
    }
    filtros = {}
    for k, v in request.args.items():
        if k in ('page', 'limit', 'q', 'order_by'):
            continue
        columna = MAPEO.get(k, k)
        filtros[columna] = v

    resultado = listarMonitoria(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(resultado), 200

@safe_controller
def cnregistrarMonitoria():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["mon_id", "mon_pro_id_fk", "mon_lot_id_fk", "mon_inm_id_fk", "mon_fecha", 
                 "mon_tipo", "mon_cantidad", "mon_saldo_anterior", "mon_saldo_actual", 
                 "mon_costo_unitario", "mon_costo_total"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    tipos_validos = ["Entrada", "Salida", "Ajuste"]
    if data["mon_tipo"] not in tipos_validos:
        return jsonify({"mensaje": f"Tipo inválido. Valores permitidos: {tipos_validos}"}), 400

    try:
        cantidad = int(data["mon_cantidad"])
        if cantidad <= 0:
            return jsonify({"mensaje": "La cantidad debe ser mayor a 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "La cantidad debe ser un número entero"}), 400

    try:
        saldo_ant = int(data["mon_saldo_anterior"])
        saldo_act = int(data["mon_saldo_actual"])
        if saldo_ant < 0 or saldo_act < 0:
            return jsonify({"mensaje": "Los saldos no pueden ser negativos"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "Los saldos deben ser números enteros"}), 400

    c = current_app.mysql.connection.cursor()
    c.execute("SELECT mon_id FROM t_monitoria WHERE mon_id = %s", (data["mon_id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un registro de monitoria con el ID {data['mon_id']}"}), 409

    c.execute("SELECT pro_id FROM t_producto WHERE pro_id = %s", (data["mon_pro_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un producto con el ID {data['mon_pro_id_fk']}"}), 404

    c.execute("SELECT lot_id FROM t_lote WHERE lot_id = %s", (data["mon_lot_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un lote con el ID {data['mon_lot_id_fk']}"}), 404

    c.execute("SELECT inm_id FROM t_inventario_movimiento WHERE inm_id = %s", (data["mon_inm_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un movimiento con el ID {data['mon_inm_id_fk']}"}), 404
    c.close()

    resultado = registrarMonitoria(
        data["mon_id"], data["mon_pro_id_fk"], data["mon_lot_id_fk"],
        data["mon_inm_id_fk"], data["mon_fecha"], data["mon_tipo"],
        data["mon_cantidad"], data["mon_saldo_anterior"], data["mon_saldo_actual"],
        data["mon_costo_unitario"], data["mon_costo_total"]
    )
    return jsonify({"mensaje": "Registro de monitoria guardado correctamente", "datos": resultado}), 201

@safe_controller
def cneditarMonitoria(id):
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    if not buscarMonitoria(id):
        return jsonify({"mensaje": f"No existe un registro de monitoria con el ID {id}"}), 404

    requerido = ["mon_pro_id_fk", "mon_lot_id_fk", "mon_inm_id_fk", "mon_fecha", "mon_tipo",
                 "mon_cantidad", "mon_saldo_anterior", "mon_saldo_actual",
                 "mon_costo_unitario", "mon_costo_total"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    tipos_validos = ["Entrada", "Salida", "Ajuste"]
    if data["mon_tipo"] not in tipos_validos:
        return jsonify({"mensaje": f"Tipo inválido. Valores permitidos: {tipos_validos}"}), 400

    try:
        cantidad = int(data["mon_cantidad"])
        if cantidad <= 0:
            return jsonify({"mensaje": "La cantidad debe ser mayor a 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "La cantidad debe ser un número entero"}), 400

    try:
        saldo_ant = int(data["mon_saldo_anterior"])
        saldo_act = int(data["mon_saldo_actual"])
        if saldo_ant < 0 or saldo_act < 0:
            return jsonify({"mensaje": "Los saldos no pueden ser negativos"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "Los saldos deben ser números enteros"}), 400

    c = current_app.mysql.connection.cursor()
    c.execute("SELECT pro_id FROM t_producto WHERE pro_id=%s", (data["mon_pro_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un producto con el ID {data['mon_pro_id_fk']}"}), 404

    c.execute("SELECT lot_id FROM t_lote WHERE lot_id=%s", (data["mon_lot_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un lote con el ID {data['mon_lot_id_fk']}"}), 404

    c.execute("SELECT inm_id FROM t_inventario_movimiento WHERE inm_id=%s", (data["mon_inm_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un movimiento con el ID {data['mon_inm_id_fk']}"}), 404
    c.close()

    resultado = editarMonitoria(
        id, data["mon_pro_id_fk"], data["mon_lot_id_fk"], data["mon_inm_id_fk"],
        data["mon_fecha"], data["mon_tipo"], data["mon_cantidad"],
        data["mon_saldo_anterior"], data["mon_saldo_actual"],
        data["mon_costo_unitario"], data["mon_costo_total"]
    )
    return jsonify({"mensaje": "Registro de monitoria actualizado correctamente", "datos": resultado}), 200

@safe_controller
def cneliminarMonitoria(id):
    if not buscarMonitoria(id):
        return jsonify({"mensaje": f"No existe un registro de monitoria con el ID {id}"}), 404

    if eliminarMonitoria(id):
        return jsonify({"mensaje": f"Registro de monitoria {id} eliminado correctamente"}), 200
    return jsonify({"mensaje": "No se pudo eliminar el registro"}), 500

@safe_controller
def cnbuscarMonitoria():
    mon_id = request.args.get("mon_id")
    if mon_id:
        resultado = buscarMonitoria(mon_id)
        if resultado:
            return jsonify(resultado), 200
        return jsonify({"mensaje": "Registro no encontrado"}), 404
    else:
        resultado = buscarMonitoria()
        return jsonify(resultado), 200
