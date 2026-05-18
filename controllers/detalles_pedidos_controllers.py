from flask import jsonify, request, current_app
from services.detalles_pedidos_service import (
    listarDetallesPedidos, registrarDetallesPedidos,
    editarDetallesPedidos, eliminarDetallesPedidos, buscarDetallePedido
)

def cnlistadodetallespedidos():
    try:
        obj = listarDetallesPedidos()
        return jsonify(obj), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnregistrardetallespedidos():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        requerido = ["det_id", "det_ped_id_fk", "det_pro_id_fk", "det_cantidad", "det_precio_unitario", "det_subtotal"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        # Validar ID no vacío
        if str(data["det_id"]).strip() == "":
            return jsonify({"mensaje": "El ID del detalle no puede estar vacío"}), 400

        # Validar cantidad positiva
        try:
            cantidad = int(data["det_cantidad"])
            if cantidad <= 0:
                return jsonify({"mensaje": "La cantidad debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "La cantidad debe ser un número entero"}), 400

        # Validar precio unitario
        try:
            precio = float(data["det_precio_unitario"])
            if precio <= 0:
                return jsonify({"mensaje": "El precio unitario debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El precio unitario debe ser un número válido"}), 400

        # Validar duplicado
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT det_id FROM t_detalle_pedido WHERE det_id = %s", (data["det_id"],))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": f"Ya existe un detalle de pedido con el ID {data['det_id']}"}), 409

        # Validar que el pedido exista
        c.execute("SELECT ped_id FROM t_pedido WHERE ped_id = %s", (data["det_ped_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un pedido con el ID {data['det_ped_id_fk']}"}), 404

        # Validar que el producto exista
        c.execute("SELECT pro_id FROM t_producto WHERE pro_id = %s", (data["det_pro_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un producto con el ID {data['det_pro_id_fk']}"}), 404
        c.close()

        resultado = registrarDetallesPedidos(
            data["det_id"],
            data["det_ped_id_fk"],
            data["det_pro_id_fk"],
            data.get("det_lot_id_fk"),
            data["det_cantidad"],
            data["det_precio_unitario"],
            data["det_subtotal"]
        )
        return jsonify({"mensaje": "Detalle de pedido registrado correctamente", "datos": resultado}), 201

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
    
def cneditardetallespedidos(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        if not buscarDetallePedido(id):
            return jsonify({"mensaje": f"No existe un detalle de pedido con el ID {id}"}), 404

        requerido = ["det_ped_id_fk", "det_pro_id_fk", "det_cantidad", "det_precio_unitario", "det_subtotal"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        try:
            cantidad = int(data["det_cantidad"])
            if cantidad <= 0:
                return jsonify({"mensaje": "La cantidad debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "La cantidad debe ser un número entero"}), 400

        try:
            precio = float(data["det_precio_unitario"])
            if precio <= 0:
                return jsonify({"mensaje": "El precio unitario debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El precio unitario debe ser un número válido"}), 400

        c = current_app.mysql.connection.cursor()
        c.execute("SELECT ped_id FROM t_pedido WHERE ped_id=%s", (data["det_ped_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un pedido con el ID {data['det_ped_id_fk']}"}), 404

        c.execute("SELECT pro_id FROM t_producto WHERE pro_id=%s", (data["det_pro_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un producto con el ID {data['det_pro_id_fk']}"}), 404
        c.close()

        resultado = editarDetallesPedidos(
            id,
            data["det_ped_id_fk"],
            data["det_pro_id_fk"],
            data.get("det_lot_id_fk"),
            data["det_cantidad"],
            data["det_precio_unitario"],
            data["det_subtotal"]
        )
        return jsonify({"mensaje": "Detalle de pedido actualizado correctamente", "datos": resultado}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def cneliminardetallespedidos(id):
    try:
        if not buscarDetallePedido(id):
            return jsonify({"mensaje": f"No existe un detalle de pedido con el ID {id}"}), 404

        if eliminarDetallesPedidos(id):
            return jsonify({"mensaje": f"Detalle de pedido {id} eliminado correctamente"}), 200
        return jsonify({"mensaje": "No se pudo eliminar el detalle"}), 500

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
