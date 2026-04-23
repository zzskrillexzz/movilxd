from flask import jsonify, request, current_app
from services.reportes_service import listarReportes, registrarReportes, editarReportes, eliminarReportes, buscarReportes

def cnlistadoreportes():
    try:
        datos = listarReportes()
        return jsonify(datos), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

import re # Importamos expresiones regulares

def cnregistrarreportes():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        # --- OJO: NORMALIZACIÓN DEL ID ---
        # Convertimos a mayúsculas y quitamos "-", "_", "." y espacios
        id_sucio = str(data.get("rep_id", ""))
        id_limpio = re.sub(r'[-_.\s]', '', id_sucio).upper() 
        # Ejemplo: "rep-001" -> "REP001"
        # ---------------------------------

        requerido = ["rep_id", "rep_tipo", "rep_fecha", "rep_usu_id_fk"]
        if any(x not in data for x in requerido):
            return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

        # Validar duplicado usando el ID LIMPIO
        c = current_app.mysql.connection.cursor()
        
        # Buscamos si existe algo que al limpiarlo sea igual (usando REPLACE en SQL)
        sql_check = """
            SELECT rep_id FROM t_reporte 
            WHERE UPPER(REPLACE(REPLACE(REPLACE(rep_id, '-', ''), '_', ''), ' ', '')) = %s
        """
        c.execute(sql_check, (id_limpio,))
        
        if c.fetchone():
            c.close()
            return jsonify({"mensaje": f"El ID '{id_sucio}' es equivalente a uno ya existente (evite duplicados por guiones o espacios)"}), 409

        # Validar que el usuario exista
        c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (data["rep_usu_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": "Usuario no encontrado"}), 404
        c.close()

        # Guardamos usando el ID normalizado para mantener orden
        resultado = registrarReportes(
            id_limpio, data["rep_tipo"], data["rep_fecha"],
            data.get("rep_parametros"), data["rep_usu_id_fk"], data.get("rep_resultado")
        )
        return jsonify({"mensaje": "Reporte registrado", "datos": resultado}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cneditarreportes():
    try:
        data = request.get_json()
        if not data or "rep_id" not in data:
            return jsonify({"mensaje": "ID de reporte requerido"}), 400

        # Validar si el reporte existe
        if not buscarReportes(data["rep_id"]):
            return jsonify({"mensaje": "El reporte no existe"}), 404

        # Validar que el usuario (FK) exista si se va a cambiar
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (data["rep_usu_id_fk"],))
        if not c.fetchone():
            c.close()
            return jsonify({"mensaje": "Usuario no encontrado"}), 404
        c.close()

        resultado = editarReportes(
            data["rep_id"], data["rep_tipo"], data["rep_fecha"],
            data.get("rep_parametros"), data["rep_usu_id_fk"], data.get("rep_resultado")
        )
        return jsonify({"mensaje": "Reporte actualizado correctamente", "datos": resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cneliminarreportes(rep_id):
    try:
        if not buscarReportes(rep_id):
            return jsonify({"mensaje": "Reporte no encontrado"}), 404
        
        resultado = eliminarReportes(rep_id)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cnbuscarreportes():
    try:
        rep_id = request.args.get("rep_id")
        if not rep_id:
            return jsonify({"mensaje": "ID de reporte requerido"}), 400
            
        resultado = buscarReportes(rep_id)
        if resultado:
            return jsonify(resultado), 200
        return jsonify({"mensaje": "Reporte no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500