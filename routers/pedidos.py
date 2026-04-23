from flask import Blueprint
from controllers.pedidos_controllers import (
    cnlistadopedidos, cnregistrarpedidos,
    cneditarpedidos, cneliminarpedidos
)

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/')
def listado_pedidos():
    return cnlistadopedidos()

@pedidos_bp.route('/', methods=["POST"])
def registrar_pedidos():
    return cnregistrarpedidos()

@pedidos_bp.route('/<string:id>', methods=["PUT"])
def editar_pedidos(id):
    return cneditarpedidos(id)

@pedidos_bp.route('/<string:id>', methods=["DELETE"])
def eliminar_pedidos(id):
    return cneliminarpedidos(id)