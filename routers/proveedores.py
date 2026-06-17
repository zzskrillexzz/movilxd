from flask import Blueprint
from services.auth_service import token_requerido
from controllers.proveedores_controllers import (
    cnlistadoproveedores, cnregistrarproveedores, cnbuscarproveedores,
    cneditarproveedores, cneliminarproveedores
)

proveedores_bp = Blueprint('proveedores', __name__)

@proveedores_bp.route('/')
@token_requerido
def listado():
    return cnlistadoproveedores()

@proveedores_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarproveedores()

@proveedores_bp.route('/buscar', methods=["GET"])
@token_requerido
def buscar():
    return cnbuscarproveedores()

@proveedores_bp.route('/', methods=["PUT"])
@token_requerido
def editar():
    return cneditarproveedores()

@proveedores_bp.route('/eliminar/<prov_id>', methods=["DELETE"])
@token_requerido
def eliminar(prov_id):
    return cneliminarproveedores(prov_id)