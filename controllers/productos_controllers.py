from flask import jsonify, request, current_app
from services.productos_service import listarProductos, registrarProductos, editarProductos

def cnListarProductos():
    try:
        datos = listarProductos()
        return jsonify(datos), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnRegistrarProductos():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        requerido = ["id", "nombre", "categoria", "descripcion", "precio", "cantidad_disponible", "proveedor_id"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        # Validar campos no vacíos
        for campo in ["id", "nombre", "categoria", "descripcion"]:
            if str(data[campo]).strip() == "":
                return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

        # Validar precio positivo
        try:
            precio = float(data["precio"])
            if precio <= 0:
                return jsonify({"mensaje": "El precio debe ser mayor a 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El precio debe ser un número válido"}), 400

        # Validar cantidad
        try:
            cantidad = int(data["cantidad_disponible"])
            if cantidad < 0:
                return jsonify({"mensaje": "La cantidad disponible no puede ser negativa"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "La cantidad disponible debe ser un número entero"}), 400

        # Validar estado
        estados_validos = ["Activo", "Descontinuado", "Suspendido"]
        if data.get("estado") and data["estado"] not in estados_validos:
            return jsonify({"mensaje": f"Estado inválido. Valores permitidos: {estados_validos}"}), 400

        # Validar duplicado por ID
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT pro_id FROM t_producto WHERE pro_id = %s", (data["id"],))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": f"Ya existe un producto con el ID {data['id']}"}), 409

        # Validar que el proveedor exista
        c.execute("SELECT prov_id FROM t_proveedor WHERE prov_id = %s", (data["proveedor_id"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un proveedor con el ID {data['proveedor_id']}"}), 404
        c.close()

        resultado = registrarProductos(data)
        return jsonify(resultado), 201

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnEditarProductos():
    try:
        data = request.get_json()
        if not data or "id" not in data:
            return jsonify({"mensaje": "ID del producto requerido"}), 400

        if "precio" in data and data["precio"] is not None:
            try:
                precio = float(data["precio"])
                if precio <= 0:
                    return jsonify({"mensaje": "El precio debe ser mayor a 0"}), 400
            except (ValueError, TypeError):
                return jsonify({"mensaje": "El precio debe ser un número válido"}), 400

        if "cantidad_disponible" in data and data["cantidad_disponible"] is not None:
            try:
                cantidad = int(data["cantidad_disponible"])
                if cantidad < 0:
                    return jsonify({"mensaje": "La cantidad no puede ser negativa"}), 400
            except (ValueError, TypeError):
                return jsonify({"mensaje": "La cantidad debe ser un número entero"}), 400

        resultado = editarProductos(data["id"], data)
        return jsonify(resultado), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
