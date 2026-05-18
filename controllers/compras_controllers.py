from flask import jsonify, request, current_app
from services.compras_service import listarCompras, registrarCompras, buscarCompras, editarCompras, eliminarCompras

def cnlistadocompras():
    try:
        datos = listarCompras()
        return jsonify(datos), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnregistrarcompras():
    try:
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

        estados_validos = ["Pendiente", "Recibida", "Cancelada"]
        if data["com_estado"] not in estados_validos:
            return jsonify({"mensaje": f"Estado inválido. Valores permitidos: {estados_validos}"}), 400

        try:
            total = float(data["com_total"])
            if total <= 0:
                return jsonify({"mensaje": "El total debe ser mayor a 0"}), 400
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

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnbuscarcompras(COM_ID):
    try:
        resultado = buscarCompras(COM_ID)
        if resultado is None:
            return jsonify({"mensaje": f"No se encontró la compra con ID {COM_ID}"}), 404
        return jsonify(resultado), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cneditarcompras(COM_ID):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        if data.get("com_estado"):
            estados_validos = ["Pendiente", "Recibida", "Cancelada"]
            if data["com_estado"] not in estados_validos:
                return jsonify({"mensaje": f"Estado inválido. Valores permitidos: {estados_validos}"}), 400

        if data.get("com_total"):
            try:
                total = float(data["com_total"])
                if total <= 0:
                    return jsonify({"mensaje": "El total debe ser mayor a 0"}), 400
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

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cneliminarcompras(COM_ID):
    try:
        compra = buscarCompras(COM_ID)
        if compra is None:
            return jsonify({"mensaje": f"No se encontró la compra con ID {COM_ID}"}), 404
        resultado = eliminarCompras(COM_ID)
        return jsonify(resultado), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
