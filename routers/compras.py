from flask import Blueprint
from services.auth_service import token_requerido
from controllers.compras_controllers import cnlistadocompras, cnregistrarcompras

compras_bp = Blueprint('compras', __name__)

@compras_bp.route('/')
@token_requerido
def listado():
    return cnlistadocompras()

@compras_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarcompras()