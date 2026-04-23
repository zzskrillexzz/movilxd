from flask import jsonify, request, current_app
from services.sesiones_service import listarSesiones, registrarSesiones, editarSesiones, eliminarSesiones, buscarSesiones

def cnlistadosesiones():
    try:
        return jsonify(listarSesiones()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cnregistrarsesiones():
    try:
        data = request.get_json()
        requerido = ["ses_id", "ses_usu_id_fk", "ses_fecha_inicio", "ses_ip", "ses_activa"]
        
        # Validar campos faltantes
        if not data or any(x not in data for x in requerido):
            return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

        # Validar si el usuario existe (FK)
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (data["ses_usu_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": "El usuario especificado no existe"}), 400

        # Validar ID duplicado
        c.execute("SELECT ses_id FROM t_sesion WHERE ses_id = %s", (data["ses_id"],))
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": "El ID de sesión ya existe"}), 409
        c.close()

        resultado = registrarSesiones(
            data["ses_id"], data["ses_usu_id_fk"], data["ses_fecha_inicio"],
            data.get("ses_fecha_fin"), data["ses_ip"], data["ses_activa"]
        )
        return jsonify({"mensaje": "Sesión registrada", "datos": resultado}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cneditarsesiones():
    try:
        data = request.get_json()
        if not data or "ses_id" not in data:
            return jsonify({"mensaje": "ID de sesión requerido"}), 400
        
        resultado = editarSesiones(
            data["ses_id"], data["ses_usu_id_fk"], data["ses_fecha_inicio"],
            data.get("ses_fecha_fin"), data["ses_ip"], data["ses_activa"]
        )
        return jsonify({"mensaje": "Sesión actualizada", "datos": resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cneliminarsesiones(ses_id):
    try:
        if not buscarSesiones(ses_id):
            return jsonify({"mensaje": "Sesión no encontrada"}), 404
        return jsonify(eliminarSesiones(ses_id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cnbuscarsesiones():
    try:
        ses_id = request.args.get("ses_id")
        resultado = buscarSesiones(ses_id)
        if resultado:
            return jsonify(resultado), 200
        return jsonify({"mensaje": "Sesión no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500