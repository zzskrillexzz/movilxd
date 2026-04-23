from flask import Blueprint
from controllers.clientes_controllers import *

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/', methods=["GET"])
def listado():
    return cnlistadoclientes()

@clientes_bp.route('/', methods=["POST"])
def registrar():
    return cnregistrarclientes()

@clientes_bp.route('/', methods=["PUT"])
def editar():
    return cneditarclientes()

@clientes_bp.route('/eliminar/<cli_id>', methods=["DELETE"])
def eliminar(cli_id):
    return cneliminarclientes(cli_id)

@clientes_bp.route('/buscar', methods=["GET"])
def buscar():
    return cnbuscarclientes()