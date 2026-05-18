from flask import Blueprint
from services.auth_service import token_requerido
from controllers.compras_controllers import cnlistadocompras, cnregistrarcompras, cnbuscarcompras, cneditarcompras, cneliminarcompras

compras_bp = Blueprint('compras', __name__)

@compras_bp.route('/')
@token_requerido
def listado():
    return cnlistadocompras()

@compras_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarcompras()

@compras_bp.route('/<COM_ID>')
@token_requerido
def buscar(COM_ID):
    return cnbuscarcompras(COM_ID)

@compras_bp.route('/<COM_ID>', methods=["PUT"])
@token_requerido
def editar(COM_ID):
    return cneditarcompras(COM_ID)

@compras_bp.route('/<COM_ID>', methods=["DELETE"])
@token_requerido
def eliminar(COM_ID):
    return cneliminarcompras(COM_ID)
