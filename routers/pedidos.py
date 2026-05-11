from flask import Blueprint
from services.auth_service import token_requerido
from controllers.pedidos_controllers import (
    cnlistadopedidos, cnregistrarpedidos,
    cneditarpedidos, cneliminarpedidos
)

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/')
@token_requerido
def listado_pedidos():
    return cnlistadopedidos()

@pedidos_bp.route('/', methods=["POST"])
@token_requerido
def registrar_pedidos():
    return cnregistrarpedidos()

@pedidos_bp.route('/<string:id>', methods=["PUT"])
@token_requerido
def editar_pedidos(id):
    return cneditarpedidos(id)

@pedidos_bp.route('/<string:id>', methods=["DELETE"])
@token_requerido
def eliminar_pedidos(id):
    return cneliminarpedidos(id)