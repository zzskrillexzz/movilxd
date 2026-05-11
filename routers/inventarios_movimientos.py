from flask import Blueprint
from services.auth_service import token_requerido
from controllers.inventarios_movimientos_controllers import cnlistadoinventariosmovimientos, cnregistrarinventariosmovimientos

inventarios_movimientos_bp = Blueprint('inventarios_movimientos', __name__)

@inventarios_movimientos_bp.route('/')
@token_requerido
def listado():
    return cnlistadoinventariosmovimientos()

@inventarios_movimientos_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarinventariosmovimientos()