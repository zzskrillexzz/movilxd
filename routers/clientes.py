from flask import Blueprint
from services.auth_service import token_requerido
from controllers.clientes_controllers import *

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/', methods=["GET"])
@token_requerido
def listado():
    return cnlistadoclientes()

@clientes_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarclientes()

@clientes_bp.route('/', methods=["PUT"])
@token_requerido
def editar():
    return cneditarclientes()

@clientes_bp.route('/eliminar/<cli_id>', methods=["DELETE"])
@token_requerido
def eliminar(cli_id):
    return cneliminarclientes(cli_id)

@clientes_bp.route('/buscar', methods=["GET"])
@token_requerido
def buscar():
    return cnbuscarclientes()