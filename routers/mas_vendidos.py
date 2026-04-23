from flask import Blueprint
from controllers.mas_vendidos_controllers import cnlistadomasvendidos

mas_vendidos_bp = Blueprint('mas_vendidos', __name__)

@mas_vendidos_bp.route('/')
def listado():
    return cnlistadomasvendidos()