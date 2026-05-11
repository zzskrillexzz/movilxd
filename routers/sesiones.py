from flask import Blueprint
from services.auth_service import token_requerido
from controllers.sesiones_controllers import cnbuscarsesiones,cneditarsesiones,cnlistadosesiones,cneliminarsesiones, cnregistrarsesiones

sesiones_bp = Blueprint('sesiones', __name__)

@sesiones_bp.route('/', methods=["GET"])
@token_requerido
def listado():
    return cnlistadosesiones()

@sesiones_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarsesiones()

@sesiones_bp.route('/', methods=["PUT"])
@token_requerido
def editar():
    return cneditarsesiones()

@sesiones_bp.route('/eliminar/<ses_id>', methods=["DELETE"])
@token_requerido
def eliminar(ses_id):
    return cneliminarsesiones(ses_id)

@sesiones_bp.route('/buscar', methods=["GET"])
@token_requerido
def buscar():
    return cnbuscarsesiones()