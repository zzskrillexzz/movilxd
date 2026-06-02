from flask import Blueprint, request, jsonify
from services.auth_service import token_requerido, rol_requerido
from controllers.proveedores_productos_controllers import (
    cnlistadoproveedoresproductos,
    cnregistrarproveedoresproductos,
    cneliminarproveedoresproductos,
    cnbuscarproductosporproveedor,
    cnbuscarproveedoresporproducto
)

proveedores_productos_bp = Blueprint('proveedores_productos', __name__)

@proveedores_productos_bp.route('/')
@token_requerido
def listado():
    return cnlistadoproveedoresproductos()

@proveedores_productos_bp.route('/', methods=["POST"])
@token_requerido
@rol_requerido('Administrador', 'Bodeguero')
def registrar():
    return cnregistrarproveedoresproductos()

# BUG-019: Rutas que estaban definidas en el controller pero sin conexión HTTP
@proveedores_productos_bp.route('/', methods=["DELETE"])
@token_requerido
@rol_requerido('Administrador', 'Bodeguero')
def eliminar():
    return cneliminarproveedoresproductos()

@proveedores_productos_bp.route('/buscar-por-proveedor/<prov_id>', methods=["GET"])
@token_requerido
def buscar_por_proveedor(prov_id):
    return cnbuscarproductosporproveedor(prov_id)

@proveedores_productos_bp.route('/buscar-por-producto/<pro_id>', methods=["GET"])
@token_requerido
def buscar_por_producto(pro_id):
    return cnbuscarproveedoresporproducto(pro_id)