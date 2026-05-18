from .clientes import clientes_bp
from .pedidos import pedidos_bp
from .facturas import facturas_bp
from .productos import productos_bp
from .detalles_pedidos import detalles_pedidos_bp
from .proveedores import proveedores_bp
from .inventarios_movimientos import inventarios_movimientos_bp
from .lotes import lotes_bp
from .compras import compras_bp
from .detalles_compras import detalles_compras_bp
from .anulaciones_ventas import anulaciones_ventas_bp
from .alertas_vencimientos import alertas_vencimientos_bp
from .monitorias import monitoria_bp
from .reportes import reportes_bp
from .sesiones import sesiones_bp
from .usuarios import usuarios_bp
from .proveedores_productos import proveedores_productos_bp
from .mas_vendidos import mas_vendidos_bp
from .documentacion import documentacion_bp
from .auth import autenticacion_bp
from .devoluciones import devoluciones_bp
from .publico import publico_bp

def cargarruta(app):
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')
    app.register_blueprint(facturas_bp, url_prefix='/facturas')
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(detalles_pedidos_bp, url_prefix='/detalles_pedidos')
    app.register_blueprint(proveedores_bp, url_prefix='/proveedores')
    app.register_blueprint(inventarios_movimientos_bp, url_prefix='/inventarios_movimientos')
    app.register_blueprint(lotes_bp, url_prefix='/lotes')
    app.register_blueprint(compras_bp, url_prefix='/compras')
    app.register_blueprint(detalles_compras_bp, url_prefix='/detalles_compras')
    app.register_blueprint(anulaciones_ventas_bp, url_prefix='/anulaciones_ventas')
    app.register_blueprint(alertas_vencimientos_bp, url_prefix='/alertas_vencimientos')
    app.register_blueprint(monitoria_bp, url_prefix='/monitorias')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    app.register_blueprint(sesiones_bp, url_prefix='/sesiones')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(proveedores_productos_bp, url_prefix='/proveedores_productos')
    app.register_blueprint(mas_vendidos_bp, url_prefix='/mas_vendidos')
    app.register_blueprint(documentacion_bp, url_prefix='/documentacion')
    app.register_blueprint(devoluciones_bp, url_prefix='/devoluciones')
    app.register_blueprint(autenticacion_bp, url_prefix='')
    app.register_blueprint(publico_bp, url_prefix='')