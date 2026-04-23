from flask import Blueprint
from controllers.reportes_controllers import cnlistadoreportes, cnregistrarreportes, cneditarreportes, cneliminarreportes, cnbuscarreportes

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/', methods=["GET"])
def listado():
    return cnlistadoreportes()

@reportes_bp.route('/', methods=["POST"])
def registrar():
    return cnregistrarreportes()

@reportes_bp.route('/', methods=["PUT"])
def editar():
    return cneditarreportes()

@reportes_bp.route('/eliminar/<rep_id>', methods=["DELETE"])
def eliminar(rep_id):
    return cneliminarreportes(rep_id)

@reportes_bp.route('/buscar', methods=["GET"])
def buscar():
    return cnbuscarreportes()