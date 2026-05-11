from flask import Blueprint
from services.auth_service import token_requerido
from controllers.detalles_pedidos_controllers import (
    cnlistadodetallespedidos, cnregistrardetallespedidos,
    cneditardetallespedidos, cneliminardetallespedidos
)

detalles_pedidos_bp = Blueprint('detalles_pedidos', __name__)

@detalles_pedidos_bp.route('/')
@token_requerido
def listado():
    return cnlistadodetallespedidos()

@detalles_pedidos_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrardetallespedidos()

@detalles_pedidos_bp.route('/<string:id>', methods=["PUT"])
@token_requerido
def editar(id):
    return cneditardetallespedidos(id)

@detalles_pedidos_bp.route('/<string:id>', methods=["DELETE"])
@token_requerido
def eliminar(id):
    return cneliminardetallespedidos(id)