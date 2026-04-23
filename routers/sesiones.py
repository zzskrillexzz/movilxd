from flask import Blueprint
from controllers.sesiones_controllers import cnbuscarsesiones,cneditarsesiones,cnlistadosesiones,cneliminarsesiones, cnregistrarsesiones

sesiones_bp = Blueprint('sesiones', __name__)

@sesiones_bp.route('/', methods=["GET"])
def listado():
    return cnlistadosesiones()

@sesiones_bp.route('/', methods=["POST"])
def registrar():
    return cnregistrarsesiones()

@sesiones_bp.route('/', methods=["PUT"])
def editar():
    return cneditarsesiones()

@sesiones_bp.route('/eliminar/<ses_id>', methods=["DELETE"])
def eliminar(ses_id):
    return cneliminarsesiones(ses_id)

@sesiones_bp.route('/buscar', methods=["GET"])
def buscar():
    return cnbuscarsesiones()