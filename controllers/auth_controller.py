from services.auth_service import login, revocarToken
from flask import request, current_app
import jwt

def iniciarSesion(USU_CORREO, USU_CONTRASENA):
    # Le delega todo al service
    resultado = login(USU_CORREO, USU_CONTRASENA)

    if not resultado:
        return None  # credenciales incorrectas o usuario inactivo

    return resultado

def cerrarSesion():
    """Revoca el token JWT actual insertándolo en la blacklist."""
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ', 1)[1].strip()

    # Decodificar sin verificar expiración para obtener el id de usuario
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=["HS256"],
            options={"verify_exp": False}
        )
    except jwt.InvalidTokenError:
        return None

    revocarToken(token, payload.get('id'))
    return True