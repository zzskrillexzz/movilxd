from flask import Blueprint
from services.auth_service import token_requerido
from controllers.detalles_compras_controllers import cnlistadodetallescompras, cnregistrardetallescompras

detalles_compras_bp = Blueprint('detalles_compras', __name__)

@detalles_compras_bp.route('/')
@token_requerido
def listado():
    return cnlistadodetallescompras()

@detalles_compras_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrardetallescompras()