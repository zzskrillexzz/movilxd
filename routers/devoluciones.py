from flask import Blueprint
from services.auth_service import token_requerido
from controllers.devoluciones_controllers import cnListarDevoluciones, cnRegistrarDevolucion

devoluciones_bp = Blueprint('devoluciones', __name__)

@devoluciones_bp.route('/')
@token_requerido
def listado():
    return cnListarDevoluciones()

@devoluciones_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnRegistrarDevolucion()
