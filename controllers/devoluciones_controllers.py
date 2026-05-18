from flask import jsonify, request, current_app
from services.devoluciones_service import listarDevoluciones, registrarDevolucion

def cnListarDevoluciones():
    try:
        return jsonify(listarDevoluciones()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cnEditarDevolucion(dev_id):
    try:
        data = request.get_json()
        if not data: return jsonify({"mensaje": "No se enviaron datos"}), 400
        from services.devoluciones_service import editarDevolucion
        result = editarDevolucion(dev_id, data.get("lote_id"), data.get("cantidad"), data.get("motivo"), data.get("fecha"))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
def cnEliminarDevolucion(dev_id):
    try:
        from services.devoluciones_service import eliminarDevolucion
        if eliminarDevolucion(dev_id):
            return jsonify({"mensaje": "Devolucion eliminada"}), 200
        return jsonify({"mensaje": "No se encontro"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
def cnRegistrarDevolucion():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos"}), 400
        requerido = ["pedido_id", "producto_id", "cantidad", "motivo", "fecha"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan: {faltantes}"}), 400
        try:
            cant = int(data["cantidad"])
            if cant <= 0:
                return jsonify({"mensaje": "La cantidad debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "Cantidad invalida"}), 400
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT pro_id FROM t_producto WHERE pro_id=%s", (data["producto_id"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": "Producto no existe"}), 404
        c.close()
        result = registrarDevolucion(
            data["pedido_id"], data["producto_id"], data.get("lote_id"),
            cant, data["motivo"], data["fecha"], data.get("usuario_id")
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
