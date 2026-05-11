from flask import Blueprint
from services.auth_service import token_requerido
from controllers.mas_vendidos_controllers import cnlistadomasvendidos

mas_vendidos_bp = Blueprint('mas_vendidos', __name__)

@mas_vendidos_bp.route('/')
@token_requerido
def listado():
    return cnlistadomasvendidos()