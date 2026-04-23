from flask import jsonify, request, current_app
from services.pedidos_service import (
    listarPedidos, registrarPedidos,
    editarPedidos, eliminarPedidos, buscarPedido
)

def cnlistadopedidos():
    try:
        x = listarPedidos()
        return jsonify(x), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnregistrarpedidos():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        requerido = ["ped_id", "ped_fecha", "ped_metodo_pago", "ped_estado_entrega", "ped_total", "ped_cli_id_fk"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        # Validar campos no vacíos
        for campo in ["ped_id", "ped_fecha", "ped_metodo_pago", "ped_estado_entrega"]:
            if str(data[campo]).strip() == "":
                return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

        # Validar método de pago
        metodos_validos = ["Efectivo", "Tarjeta", "Nequi", "Daviplata", "Transferencia"]
        if data["ped_metodo_pago"] not in metodos_validos:
            return jsonify({"mensaje": f"Método de pago inválido. Valores permitidos: {metodos_validos}"}), 400

        # Validar estado entrega
        estados_validos = ["Entregado", "En camino", "No entregado", "Anulado"]
        if data["ped_estado_entrega"] not in estados_validos:
            return jsonify({"mensaje": f"Estado de entrega inválido. Valores permitidos: {estados_validos}"}), 400

        # Validar total positivo
        try:
            total = float(data["ped_total"])
            if total <= 0:
                return jsonify({"mensaje": "El total debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El total debe ser un número válido"}), 400

        # Validar duplicado
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT ped_id FROM t_pedido WHERE ped_id = %s", (data["ped_id"],))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": f"Ya existe un pedido con el ID {data['ped_id']}"}), 409

        # Validar que el cliente exista
        c.execute("SELECT cli_id FROM t_cliente WHERE cli_id = %s", (data["ped_cli_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un cliente con el ID {data['ped_cli_id_fk']}"}), 404

        # Validar que el usuario exista (si se envía)
        fk_usuario = data.get("ped_usu_id_fk")
        if fk_usuario:
            c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (fk_usuario,))
            if not c.fetchone():
                c.close()
                return jsonify({"mensaje": f"No existe un usuario con el ID {fk_usuario}"}), 404
        c.close()

        resultado = registrarPedidos(
            data["ped_id"], data["ped_fecha"], data["ped_metodo_pago"],
            data["ped_estado_entrega"], data["ped_total"], data["ped_cli_id_fk"], fk_usuario
        )
        return jsonify({"mensaje": "Pedido realizado correctamente", "datos": resultado}), 201

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cneditarpedidos(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        # Verificar que el pedido exista
        if not buscarPedido(id):
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        requerido = ["ped_fecha", "ped_metodo_pago", "ped_estado_entrega", "ped_total", "ped_cli_id_fk"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        metodos_validos = ["Efectivo", "Tarjeta", "Nequi", "Daviplata", "Transferencia"]
        if data["ped_metodo_pago"] not in metodos_validos:
            return jsonify({"mensaje": f"Método de pago inválido. Valores permitidos: {metodos_validos}"}), 400

        estados_validos = ["Entregado", "En camino", "No entregado", "Anulado"]
        if data["ped_estado_entrega"] not in estados_validos:
            return jsonify({"mensaje": f"Estado de entrega inválido. Valores permitidos: {estados_validos}"}), 400

        try:
            total = float(data["ped_total"])
            if total <= 0:
                return jsonify({"mensaje": "El total debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El total debe ser un número válido"}), 400

        c = current_app.mysql.connection.cursor()
        c.execute("SELECT cli_id FROM t_cliente WHERE cli_id=%s", (data["ped_cli_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un cliente con el ID {data['ped_cli_id_fk']}"}), 404

        fk_usuario = data.get("ped_usu_id_fk")
        if fk_usuario:
            c.execute("SELECT usu_id FROM t_usuario WHERE usu_id=%s", (fk_usuario,))
            if not c.fetchone():
                c.close()
                return jsonify({"mensaje": f"No existe un usuario con el ID {fk_usuario}"}), 404
        c.close()

        resultado = editarPedidos(
            id, data["ped_fecha"], data["ped_metodo_pago"], data["ped_estado_entrega"],
            data["ped_total"], data["ped_cli_id_fk"], fk_usuario
        )
        return jsonify({"mensaje": "Pedido actualizado correctamente", "datos": resultado}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def cneliminarpedidos(id):
    try:
        if not buscarPedido(id):
            return jsonify({"mensaje": f"No existe un pedido con el ID {id}"}), 404

        # Verificar si el pedido tiene detalles asociados
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT det_id FROM t_detalle_pedido WHERE det_ped_id_fk=%s LIMIT 1", (id,))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": "No se puede eliminar: el pedido tiene detalles asociados"}), 409
        c.close()

        if eliminarPedidos(id):
            return jsonify({"mensaje": f"Pedido {id} eliminado correctamente"}), 200
        return jsonify({"mensaje": "No se pudo eliminar el pedido"}), 500

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
