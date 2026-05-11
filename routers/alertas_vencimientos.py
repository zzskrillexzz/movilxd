from flask import Blueprint
from services.auth_service import token_requerido
from controllers.alertas_vencimientos_controllers import cnlistadoalertasvencimientos, cnregistraralertasvencimientos

alertas_vencimientos_bp = Blueprint('alertas_vencimientos', __name__)

@alertas_vencimientos_bp.route('/')
@token_requerido
def listado():
    return cnlistadoalertasvencimientos()

@alertas_vencimientos_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistraralertasvencimientos()