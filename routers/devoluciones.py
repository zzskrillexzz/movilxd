from flask import Blueprint
from services.auth_service import token_requerido
from controllers.devoluciones_controllers import cnListarDevoluciones, cnRegistrarDevolucion, cnEditarDevolucion, cnEliminarDevolucion

devoluciones_bp = Blueprint('devoluciones', __name__)

@devoluciones_bp.route('/')
@token_requerido
def listado():
    return cnListarDevoluciones()

@devoluciones_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnRegistrarDevolucion()

@devoluciones_bp.route('/<dev_id>', methods=["PUT"])
@token_requerido
def editar(dev_id):
    return cnEditarDevolucion(dev_id)

@devoluciones_bp.route('/<dev_id>', methods=["DELETE"])
@token_requerido
def eliminar(dev_id):
    return cnEliminarDevolucion(dev_id)
