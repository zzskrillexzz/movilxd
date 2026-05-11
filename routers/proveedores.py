from flask import Blueprint
from services.auth_service import token_requerido
from controllers.proveedores_controllers import cnlistadoproveedores, cnregistrarproveedores

proveedores_bp = Blueprint('proveedores', __name__)

@proveedores_bp.route('/')
@token_requerido
def listado():
    return cnlistadoproveedores()

@proveedores_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarproveedores()