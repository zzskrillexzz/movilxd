from flask import jsonify, request, current_app
from services.roles_services import listarRoles, registrarRoles, editarRoles, eliminarRoles, buscarRoles

def cnListarRoles():
    try:
        datos = listarRoles()
        return jsonify(datos), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnRegistrarRoles():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        requerido = ["id", "nombre"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        # Validar campos no vacíos
        for campo in ["id", "nombre"]:
            if str(data[campo]).strip() == "":
                return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

        # Validar estado
        if data.get("estado") not in [0, 1, None]:
            return jsonify({"mensaje": "El estado debe ser 0 (Inactivo) o 1 (Activo)"}), 400

        # Validar duplicado por ID
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT rol_id FROM t_rol WHERE rol_id = %s", (data["id"],))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": f"Ya existe un rol con el ID {data['id']}"}), 409
        c.close()

        resultado = registrarRoles(data)
        return jsonify(resultado), 201

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnEditarRoles():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        if "id" not in data:
            return jsonify({"mensaje": "El campo 'id' es requerido para editar"}), 400

        # Validar campos no vacíos
        if str(data.get("nombre", "")).strip() == "":
            return jsonify({"mensaje": "El campo nombre no puede estar vacío"}), 400

        # Validar que el rol exista
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT rol_id FROM t_rol WHERE rol_id = %s", (data["id"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un rol con el ID {data['id']}"}), 404
        c.close()

        # Validar estado
        if data.get("estado") not in [0, 1, None]:
            return jsonify({"mensaje": "El estado debe ser 0 (Inactivo) o 1 (Activo)"}), 400

        resultado = editarRoles(data)
        return jsonify(resultado), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnEliminarRoles(rol_id):
    try:
        # Validar que el rol exista
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT rol_id FROM t_rol WHERE rol_id = %s", (rol_id,))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": f"No existe un rol con el ID {rol_id}"}), 404
        c.close()

        resultado = eliminarRoles(rol_id)
        
        if resultado.get("error"):
            return jsonify({"mensaje": resultado["mensaje"]}), 409
        
        return jsonify(resultado), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnBuscarRoles():
    try:
        rol_id = request.args.get("rol_id")
        if not rol_id:
            return jsonify({"mensaje": "Debe proporcionar un ID de rol"}), 400
        
        resultado = buscarRoles(rol_id)
        if resultado:
            return jsonify(resultado), 200
        return jsonify({"mensaje": "Rol no encontrado"}), 404

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500