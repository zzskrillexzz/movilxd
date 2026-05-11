from flask import Blueprint
from services.auth_service import token_requerido
from controllers.reportes_controllers import cnlistadoreportes, cnregistrarreportes, cneditarreportes, cneliminarreportes, cnbuscarreportes

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/', methods=["GET"])
@token_requerido
def listado():
    return cnlistadoreportes()

@reportes_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarreportes()

@reportes_bp.route('/', methods=["PUT"])
@token_requerido
def editar():
    return cneditarreportes()

@reportes_bp.route('/eliminar/<rep_id>', methods=["DELETE"])
@token_requerido
def eliminar(rep_id):
    return cneliminarreportes(rep_id)

@reportes_bp.route('/buscar', methods=["GET"])
@token_requerido
def buscar():
    return cnbuscarreportes()