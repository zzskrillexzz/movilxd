from flask import jsonify, request, current_app
from services.devoluciones_service import listarDevoluciones, registrarDevolucion
from utils.validators import validar_campos_texto
from utils.error_handler import safe_controller

@safe_controller
def cnListarDevoluciones():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    return jsonify(listarDevoluciones(page=page, limit=limit, q=q, order_by=order_by, **filtros)), 200

@safe_controller
def cnEditarDevolucion(dev_id):
    data = request.get_json()
    if not data: return jsonify({"mensaje": "No se enviaron datos"}), 400
    from services.devoluciones_service import editarDevolucion
    result = editarDevolucion(dev_id, data.get("lote_id"), data.get("cantidad"), data.get("motivo"), data.get("fecha"))
    return jsonify(result), 200
@safe_controller
def cnEliminarDevolucion(dev_id):
    from services.devoluciones_service import eliminarDevolucion
    if eliminarDevolucion(dev_id):
        return jsonify({"mensaje": "Devolucion eliminada"}), 200
    return jsonify({"mensaje": "No se encontro"}), 404
@safe_controller
def cnRegistrarDevolucion():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos"}), 400
    requerido = ["compra_id", "producto_id", "cantidad", "motivo", "fecha"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan: {faltantes}"}), 400
    try:
        cant = int(data["cantidad"])
        if cant <= 0:
            return jsonify({"mensaje": "La cantidad debe ser mayor a 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "Cantidad invalida"}), 400

    # Validar longitud del motivo
    msg = validar_campos_texto(data, "motivo")
    if msg:
        return jsonify({"mensaje": " | ".join(msg)}), 400

    c = current_app.mysql.connection.cursor()
    c.execute("SELECT pro_id FROM t_producto WHERE pro_id=%s", (data["producto_id"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": "Producto no existe"}), 404
    # Validar que la compra exista
    c.execute("SELECT com_id FROM t_compra WHERE com_id=%s", (data["compra_id"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": "La compra no existe"}), 404
    c.close()
    try:
        result = registrarDevolucion(
            data["compra_id"], data["producto_id"], data.get("lote_id"),
            cant, data["motivo"], data["fecha"], data.get("usuario_id")
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"mensaje": str(e)}), 400
