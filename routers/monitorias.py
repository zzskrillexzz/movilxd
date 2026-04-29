from flask import Blueprint
from controllers.monitorias_controllers import (
    cnlistarMonitoria,
    cnregistrarMonitoria,
    cneditarMonitoria,
    cneliminarMonitoria,
    cnbuscarMonitoria
)

monitoria_bp = Blueprint('monitoria', __name__)

@monitoria_bp.route('/', methods=['GET'])
def listar():
    return cnlistarMonitoria()

@monitoria_bp.route('/', methods=['POST'])
def registrar():
    return cnregistrarMonitoria()

@monitoria_bp.route('/<id>', methods=['PUT'])
def editar(id):
    return cneditarMonitoria(id)

@monitoria_bp.route('/<id>', methods=['DELETE'])
def eliminar(id):
    return cneliminarMonitoria(id)

@monitoria_bp.route('/buscar', methods=['GET'])
def buscar():
    return cnbuscarMonitoria()