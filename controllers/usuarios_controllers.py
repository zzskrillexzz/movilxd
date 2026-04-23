from flask import jsonify, request, current_app
from services.usuarios_service import listarUsuarios, registrarUsuarios, editarUsuarios, eliminarUsuarios, buscarUsuarios

def cnlistadousuarios():
    try:
        datos = listarUsuarios()
        return jsonify(datos), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def cnregistrarusuarios():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        requerido = ["usu_id", "usu_nombre", "usu_rol", "usu_correo", "usu_contrasena", "usu_estado"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        # Validar campos no vacíos
        for campo in ["usu_id", "usu_nombre", "usu_rol", "usu_correo", "usu_contrasena"]:
            if str(data[campo]).strip() == "":
                return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

        # Validar rol
        roles_validos = ["Administrador", "Vendedor", "Bodeguero", "Contador"]
        if data["usu_rol"] not in roles_validos:
            return jsonify({"mensaje": f"Rol inválido. Valores permitidos: {roles_validos}"}), 400

        # Validar estado
        if data["usu_estado"] not in [0, 1]:
            return jsonify({"mensaje": "El estado debe ser 0 (Inactivo) o 1 (Activo)"}), 400

        # Validar duplicado por ID
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (data["usu_id"],))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": f"Ya existe un usuario con el ID {data['usu_id']}"}), 409

        # Validar correo duplicado
        c.execute("SELECT usu_id FROM t_usuario WHERE usu_correo = %s", (data["usu_correo"],))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": f"Ya existe un usuario con el correo {data['usu_correo']}"}), 409
        c.close()

        ultimo_acceso = data.get("usu_ultimo_acceso")

        resultado = registrarUsuarios(
            data["usu_id"], data["usu_nombre"], data["usu_rol"],
            data["usu_correo"], data["usu_contrasena"], data["usu_estado"], ultimo_acceso
        )
        return jsonify({"mensaje": "Usuario registrado correctamente", "datos": resultado}), 201

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def cneditarusuarios():
    try:
        data = request.get_json()
        if not data or "usu_id" not in data:
            return jsonify({"mensaje": "Se requiere el ID del usuario"}), 400

        # Validar campos requeridos para la edición
        requerido = ["usu_nombre", "usu_rol", "usu_correo", "usu_contrasena", "usu_estado"]
        faltantes = [x for x in requerido if x not in data]
        if faltantes:
            return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

        # Validar campos no vacíos
        for campo in requerido:
            if str(data[campo]).strip() == "":
                return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

        # Validar rol y estado
        roles_validos = ["Administrador", "Vendedor", "Bodeguero", "Contador"]
        if data["usu_rol"] not in roles_validos:
            return jsonify({"mensaje": f"Rol inválido"}), 400
        if data["usu_estado"] not in [0, 1]:
            return jsonify({"mensaje": "El estado debe ser 0 o 1"}), 400

        # Verificar existencia y validar duplicidad de correo (que no sea de otro ID)
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT usu_id FROM t_usuario WHERE usu_correo = %s AND usu_id != %s", (data["usu_correo"], data["usu_id"]))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": "El correo ya está en uso por otro usuario"}), 409
        c.close()

        resultado = editarUsuarios(
            data["usu_id"], data["usu_nombre"], data["usu_rol"],
            data["usu_correo"], data["usu_contrasena"], data["usu_estado"], data.get("usu_ultimo_acceso")
        )
        return jsonify({"mensaje": "Usuario actualizado correctamente", "datos": resultado}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def cneliminarusuarios(usu_id):
    try:
        # El usu_id viene de la URL, no del JSON
        usuario = buscarUsuarios(usu_id)
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        eliminarUsuarios(usu_id)
        return jsonify({"mensaje": "Usuario eliminado", "id": usu_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
def cnbuscarusuarios():
    try:
        # Obtenemos el ID desde los parámetros de la URL (Query String) ?usu_id=...
        usu_id = request.args.get("usu_id")
        
        if not usu_id:
            return jsonify({"mensaje": "Debe proporcionar un ID de usuario"}), 400

        usuario = buscarUsuarios(usu_id)
        
        if usuario:
            return jsonify(usuario), 200
        else:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500