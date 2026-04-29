from flask import Blueprint
from controllers.monitorias_controllers import (
    cnlistadomonitorias,
    cnregistrarmonitorias,
    cneditarmonitorias,
    cneliminarmonitorias,
    cnbuscarmonitorias
)

monitorias_bp = Blueprint('monitorias', __name__)

@monitorias_bp.route('/', methods=['GET'])
def listar_monitorias():
    return cnlistadomonitorias()

@monitorias_bp.route('/', methods=['POST'])
def registrar_monitorias():
    return cnregistrarmonitorias()

@monitorias_bp.route('/<id>', methods=['PUT'])
def editar_monitorias(id):
    return cneditarmonitorias(id)

@monitorias_bp.route('/<id>', methods=['DELETE'])
def eliminar_monitorias(id):
    return cneliminarmonitorias(id)

@monitorias_bp.route('/buscar', methods=['GET'])
def buscar_monitorias():
    return cnbuscarmonitorias()