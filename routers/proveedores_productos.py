from flask import Blueprint
from services.auth_service import token_requerido
from controllers.proveedores_productos_controllers import cnlistadoproveedoresproductos, cnregistrarproveedoresproductos

proveedores_productos_bp = Blueprint('proveedores_productos', __name__)

@proveedores_productos_bp.route('/')
@token_requerido
def listado():
    return cnlistadoproveedoresproductos()

@proveedores_productos_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarproveedoresproductos()