from flask import Blueprint
from controllers.kardex_controllers import (
    cnlistadokardex,
    cnregistrarkardex,
    cneditarkardex,
    cneliminarkardex,
    cnbuscarkardex
)

kardex_bp = Blueprint('kardex', __name__)

@kardex_bp.route('/', methods=['GET'])
def listar_kardex():
    return cnlistadokardex()

@kardex_bp.route('/', methods=['POST'])
def registrar_kardex():
    return cnregistrarkardex()

@kardex_bp.route('/<id>', methods=['PUT'])
def editar_kardex(id):
    return cneditarkardex(id)

@kardex_bp.route('/<id>', methods=['DELETE'])
def eliminar_kardex(id):
    return cneliminarkardex(id)

@kardex_bp.route('/buscar', methods=['GET'])
def buscar_kardex():
    return cnbuscarkardex()