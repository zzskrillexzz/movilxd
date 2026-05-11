from flask import Blueprint
from services.auth_service import token_requerido
from controllers.monitorias_controllers import (
    cnlistarMonitoria,
    cnregistrarMonitoria,
    cneditarMonitoria,
    cneliminarMonitoria,
    cnbuscarMonitoria
)

monitoria_bp = Blueprint('monitoria', __name__)

@monitoria_bp.route('/', methods=['GET'])
@token_requerido
def listar():
    return cnlistarMonitoria()

@monitoria_bp.route('/', methods=['POST'])
@token_requerido
def registrar():
    return cnregistrarMonitoria()

@monitoria_bp.route('/<id>', methods=['PUT'])
@token_requerido
def editar(id):
    return cneditarMonitoria(id)

@monitoria_bp.route('/<id>', methods=['DELETE'])
@token_requerido
def eliminar(id):
    return cneliminarMonitoria(id)

@monitoria_bp.route('/buscar', methods=['GET'])
@token_requerido
def buscar():
    return cnbuscarMonitoria()