from flask import Blueprint, request, jsonify
from controllers.auth_controller import iniciarSesion, cerrarSesion
from services.auth_service import token_requerido, rate_limit, refrescarToken

autenticacion_bp = Blueprint('autenticacion', __name__)

@autenticacion_bp.route('/login', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60)
def login():
    # 1. Recibe los datos del frontend
    body = request.get_json()
    
    # BUG-014: Validar que body sea un dict
    if not isinstance(body, dict):
        return jsonify({"error": "Body inválido", "detalle": "Se esperaba un objeto JSON"}), 400
    
    correo   = body.get('usu_correo')
    password = body.get('usu_contrasena')

    # 2. Le pregunta al controller
    resultado = iniciarSesion(correo, password)

    # 3. ¿Falló?
    if not resultado:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    # 4. ¿Todo ok?
    return jsonify(resultado), 200

# BUG-020: Endpoint para refrescar token
@autenticacion_bp.route('/refresh', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def refresh():
    body = request.get_json()
    if not isinstance(body, dict):
        return jsonify({"error": "Body inválido", "detalle": "Se esperaba un objeto JSON con 'refresh_token'"}), 400
    
    refresh_token = body.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "Refresh token requerido"}), 400
    
    resultado = refrescarToken(refresh_token)
    if not resultado:
        return jsonify({"error": "Refresh token inválido o expirado"}), 401
    
    return jsonify(resultado), 200


@autenticacion_bp.route('/logout', methods=['POST'])
@token_requerido
def logout():
    resultado = cerrarSesion()
    if not resultado:
        return jsonify({"error": "No se pudo cerrar la sesión"}), 500
    return jsonify({"mensaje": "Sesión cerrada correctamente"}), 200