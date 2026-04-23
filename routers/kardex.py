from flask import Blueprint
from controllers.kardex_controllers import (
    cnlistadokardex, cnregistrarkardex,
    cneditarkardex, cneliminarkardex
)

kardex_bp = Blueprint('kardex', __name__)

@kardex_bp.route('/')
def listado():
    return cnlistadokardex()

@kardex_bp.route('/', methods=["POST"])
def registrar():
    return cnregistrarkardex()

@kardex_bp.route('/<string:id>', methods=["PUT"])
def editar(id):
    return cneditarkardex(id)

@kardex_bp.route('/<string:id>', methods=["DELETE"])
def eliminar(id):
    return cneliminarkardex(id)