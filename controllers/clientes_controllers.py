from flask import jsonify, request, current_app
from services.clientes_service import listarClientes, registrarClientes, editarClientes, eliminarClientes, buscarClientes

def cnlistadoclientes():
    try:
        return jsonify(listarClientes()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cnregistrarclientes():
    try:
        data = request.get_json()
        requerido = ["cli_id", "cli_tipo_documento", "cli_nombre", "cli_apellido", "cli_correo"]
        
        if not data or any(x not in data for x in requerido):
            return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

        # Validar que cli_id sea un entero positivo
        try:
            cli_id = int(data["cli_id"])
            if cli_id <= 0:
                return jsonify({"mensaje": "El ID del cliente debe ser un número positivo"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El ID del cliente debe ser un número entero"}), 400

        # Validar ID duplicado
        if buscarClientes(data["cli_id"]):
            return jsonify({"mensaje": f"El cliente con ID {data['cli_id']} ya existe"}), 409

        # Validar Correo duplicado
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT cli_id FROM t_cliente WHERE cli_correo = %s", (data["cli_correo"],))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": "El correo ya está registrado"}), 409
        c.close()

        resultado = registrarClientes(
            data["cli_id"], data["cli_tipo_documento"], data["cli_nombre"],
            data["cli_apellido"], data.get("cli_telefono"), data.get("cli_direccion"), data["cli_correo"]
        )
        return jsonify({"mensaje": "Cliente registrado", "datos": resultado}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cneditarclientes():
    try:
        data = request.get_json()
        if not data or "cli_id" not in data:
            return jsonify({"mensaje": "ID de cliente requerido"}), 400

        # Validar que cli_id sea un entero positivo
        try:
            cli_id = int(data["cli_id"])
            if cli_id <= 0:
                return jsonify({"mensaje": "El ID del cliente debe ser un número positivo"}), 400
        except (ValueError, TypeError):
            return jsonify({"mensaje": "El ID del cliente debe ser un número entero"}), 400

        # Validar que el correo no lo tenga otro cliente
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT cli_id FROM t_cliente WHERE cli_correo = %s AND cli_id != %s", (data["cli_correo"], data["cli_id"]))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": "El correo ya pertenece a otro cliente"}), 409
        c.close()

        resultado = editarClientes(
            data["cli_id"], data["cli_tipo_documento"], data["cli_nombre"],
            data["cli_apellido"], data.get("cli_telefono"), data.get("cli_direccion"), data["cli_correo"]
        )
        return jsonify({"mensaje": "Cliente actualizado", "datos": resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cneliminarclientes(cli_id):
    try:
        if not buscarClientes(cli_id):
            return jsonify({"mensaje": "Cliente no encontrado"}), 404
        return jsonify(eliminarClientes(cli_id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cnbuscarclientes():
    try:
        cli_id = request.args.get("cli_id")
        resultado = buscarClientes(cli_id)
        if resultado:
            return jsonify(resultado), 200
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500