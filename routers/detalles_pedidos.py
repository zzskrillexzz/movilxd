from flask import Blueprint
from controllers.detalles_pedidos_controllers import (
    cnlistadodetallespedidos, cnregistrardetallespedidos,
    cneditardetallespedidos, cneliminardetallespedidos
)

detalles_pedidos_bp = Blueprint('detalles_pedidos', __name__)

@detalles_pedidos_bp.route('/')
def listado():
    return cnlistadodetallespedidos()

@detalles_pedidos_bp.route('/', methods=["POST"])
def registrar():
    return cnregistrardetallespedidos()

@detalles_pedidos_bp.route('/<string:id>', methods=["PUT"])
def editar(id):
    return cneditardetallespedidos(id)

@detalles_pedidos_bp.route('/<string:id>', methods=["DELETE"])
def eliminar(id):
    return cneliminardetallespedidos(id)