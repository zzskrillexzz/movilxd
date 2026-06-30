from flask import jsonify, request, current_app
from services.detalles_compras_service import (
    listarDetallesCompras, registrarDetallesCompras,
    buscarDetallesCompras, editarDetallesCompras, eliminarDetallesCompras
)
from utils.error_handler import safe_controller

@safe_controller
def cnlistadodetallescompras():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarDetallesCompras(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnregistrardetallescompras():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["dco_id", "dco_com_id_fk", "dco_pro_id_fk", "dco_cantidad", "dco_precio_compra", "dco_subtotal"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    # Validar cantidad positiva
    try:
        cantidad = int(data["dco_cantidad"])
        if cantidad <= 0:
            return jsonify({"mensaje": "La cantidad debe ser mayor a 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "La cantidad debe ser un número entero"}), 400

    # Validar precio positivo
    try:
        precio = float(data["dco_precio_compra"])
        if precio <= 0:
            return jsonify({"mensaje": "El precio de compra debe ser mayor a 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"mensaje": "El precio de compra debe ser un número válido"}), 400

    # Validar duplicado
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT dco_id FROM t_detalle_compra WHERE dco_id = %s", (data["dco_id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un detalle de compra con el ID {data['dco_id']}"}), 409

    # Validar que la compra exista
    c.execute("SELECT com_id FROM t_compra WHERE com_id = %s", (data["dco_com_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe una compra con el ID {data['dco_com_id_fk']}"}), 404

    # Validar que el producto exista
    c.execute("SELECT pro_id FROM t_producto WHERE pro_id = %s", (data["dco_pro_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un producto con el ID {data['dco_pro_id_fk']}"}), 404

    # Validar que el lote exista (si se proporcionó)
    dco_lot_id = data.get("dco_lot_id_fk")
    if dco_lot_id:
        c.execute("SELECT lot_id FROM t_lote WHERE lot_id = %s", (dco_lot_id,))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un lote con el ID {dco_lot_id}"}), 404

    # Obtener proveedor de la compra (necesario para auto-crear lote)
    dco_prov_id_fk = None
    dco_fecha_fabricacion = data.get("dco_fecha_fabricacion")
    dco_fecha_vencimiento = data.get("dco_fecha_vencimiento")
    if not dco_lot_id and dco_fecha_fabricacion and dco_fecha_vencimiento:
        c.execute("SELECT com_prov_id_fk FROM t_compra WHERE com_id = %s", (data["dco_com_id_fk"],))
        row = c.fetchone()
        if row:
            dco_prov_id_fk = row[0]
    c.close()

    resultado = registrarDetallesCompras(
        data["dco_id"], data["dco_com_id_fk"], data["dco_pro_id_fk"],
        dco_lot_id, data["dco_cantidad"], data["dco_precio_compra"], data["dco_subtotal"],
        dco_fecha_fabricacion, dco_fecha_vencimiento, dco_prov_id_fk
    )
    return jsonify({"mensaje": "Detalle de compra registrado correctamente (inventario actualizado)", "datos": resultado}), 201


@safe_controller
def cnbuscadetallescompras(DCO_ID):
    resultado = buscarDetallesCompras(DCO_ID)
    if resultado is None:
        return jsonify({"mensaje": f"No se encontró el detalle de compra con ID {DCO_ID}"}), 404
    return jsonify(resultado), 200


@safe_controller
def cneditardetallescompras(DCO_ID):
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    if not buscarDetallesCompras(DCO_ID):
        return jsonify({"mensaje": f"No se encontró el detalle de compra con ID {DCO_ID}"}), 404

    resultado = editarDetallesCompras(DCO_ID, data)
    return jsonify(resultado), 200


@safe_controller
def cneliminardetallescompras(DCO_ID):
    if not buscarDetallesCompras(DCO_ID):
        return jsonify({"mensaje": f"No se encontró el detalle de compra con ID {DCO_ID}"}), 404

    try:
        if eliminarDetallesCompras(DCO_ID):
            return jsonify({"mensaje": f"Detalle de compra {DCO_ID} eliminado (inventario revertido)"}), 200
        return jsonify({"mensaje": "No se pudo eliminar el detalle de compra"}), 500
    except ValueError as e:
        return jsonify({"mensaje": str(e)}), 400
