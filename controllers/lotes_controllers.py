from flask import jsonify, request, current_app
from services.lotes_service import listarLotes, registrarLotes, editarLotes

def cnlistadolotes():
    try:
        datos = listarLotes()
        return jsonify(datos), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnregistrarlotes():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        requerido = ["lot_id", "lot_numero", "lot_fecha_fabricacion", "lot_fecha_vencimiento", "lot_cantidad_inicial", "lot_cantidad_actual", "lot_pro_id_fk", "lot_prov_id_fk", "lot_estado"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        # Validar estado
        estados_validos = ["Activo", "Agotado", "Vencido", "Cuarentena"]
        if data["lot_estado"] not in estados_validos:
            return jsonify({"mensaje": f"Estado inválido. Valores permitidos: {estados_validos}"}), 400

        # Validar cantidades positivas
        try:
            cant_ini = int(data["lot_cantidad_inicial"])
            cant_act = int(data["lot_cantidad_actual"])
            if cant_ini <= 0:
                return jsonify({"mensaje": "La cantidad inicial debe ser mayor a 0"}), 400
            if cant_act < 0:
                return jsonify({"mensaje": "La cantidad actual no puede ser negativa"}), 400
            if cant_act > cant_ini:
                return jsonify({"mensaje": "La cantidad actual no puede ser mayor a la cantidad inicial"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "Las cantidades deben ser números enteros"}), 400

        # Validar duplicado
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT lot_id FROM t_lote WHERE lot_id = %s", (data["lot_id"],))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": f"Ya existe un lote con el ID {data['lot_id']}"}), 409

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
        c.close()

        resultado = registrarLotes(
            data["lot_id"], data["lot_numero"], data["lot_fecha_fabricacion"],
            data["lot_fecha_vencimiento"], data["lot_cantidad_inicial"], data["lot_cantidad_actual"],
            data["lot_pro_id_fk"], data["lot_prov_id_fk"], data["lot_estado"]
        )
        return jsonify({"mensaje": "Lote registrado correctamente", "datos": resultado}), 201

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnEditarlotes():
    try:
        data = request.get_json()
        if not data or "lot_id" not in data:
            return jsonify({"mensaje": "ID del lote requerido"}), 400

        if "lot_cantidad_inicial" in data and data["lot_cantidad_inicial"] is not None:
            try:
                cant = int(data["lot_cantidad_inicial"])
                if cant <= 0:
                    return jsonify({"mensaje": "La cantidad inicial debe ser mayor a 0"}), 400
            except (ValueError, TypeError):
                return jsonify({"mensaje": "La cantidad inicial debe ser un numero entero"}), 400

        if "lot_cantidad_actual" in data and data["lot_cantidad_actual"] is not None:
            try:
                cant = int(data["lot_cantidad_actual"])
                if cant < 0:
                    return jsonify({"mensaje": "La cantidad actual no puede ser negativa"}), 400
            except (ValueError, TypeError):
                return jsonify({"mensaje": "La cantidad actual debe ser un numero entero"}), 400

        resultado = editarLotes(data["lot_id"], data)
        return jsonify(resultado), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
