from flask import Blueprint, current_app, jsonify, request, g, send_file
from controllers.pedidos_controllers import cnconfirmarentrega
from services.auth_service import token_requerido
import time, os, subprocess, tempfile
from collections import defaultdict
from datetime import date, timedelta

publico_bp = Blueprint('publico', __name__)

# ── Rate limiter simple en memoria (5 req/min por IP) ──
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_MAX = 5
_RATE_LIMIT_WINDOW = 60  # segundos

def _check_rate_limit(ip: str) -> bool:
    ahora = time.time()
    ventana = [t for t in _rate_limit_store[ip] if ahora - t < _RATE_LIMIT_WINDOW]
    _rate_limit_store[ip] = ventana
    if len(ventana) >= _RATE_LIMIT_MAX:
        return False
    _rate_limit_store[ip].append(ahora)
    # Limpiar IPs expiradas periódicamente
    if len(_rate_limit_store) > 1000:
        for k in list(_rate_limit_store.keys()):
            _rate_limit_store[k] = [t for t in _rate_limit_store[k] if ahora - t < _RATE_LIMIT_WINDOW]
            if not _rate_limit_store[k]:
                del _rate_limit_store[k]
    return True


@publico_bp.route('/')
def index():
    return jsonify({"mensaje": "API San Diego Distribuidora - Sistema de Pedidos", "estado": "online"}), 200

@publico_bp.route('/health')
def health_check():
    """Verifica que MySQL (XAMPP) esté accesible."""
    try:
        c = current_app.mysql.connection.cursor()
        c.execute("SELECT 1")
        c.close()
        return jsonify({"db": "conectada", "estado": "online"}), 200
    except Exception as e:
        return jsonify({"db": "desconectada", "error": str(e), "estado": "degradado"}), 503

@publico_bp.route('/verificar/<pedido_id>')
def verificar_estado(pedido_id):
    """Endpoint público para verificar estado de un pedido (con rate limit)."""
    ip = request.remote_addr or '127.0.0.1'
    if not _check_rate_limit(ip):
        return jsonify({"error": "Demasiadas solicitudes. Intente de nuevo en un minuto."}), 429

    from services.pedidos_service import buscarPedido
    pedido = buscarPedido(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify({
        "ped_id": pedido.get("ped_id"),
        "ped_estado_entrega": pedido.get("ped_estado_entrega"),
        "ped_estado_pago": pedido.get("ped_estado_pago"),
        "ped_token_entrega": pedido.get("ped_token_entrega")
    }), 200

@publico_bp.route('/dashboard/resumen')
@token_requerido
def dashboard_resumen():
    """
    Endpoint agregado que devuelve todos los datos del dashboard en una sola llamada.
    """
    c = current_app.mysql.connection.cursor()
    hoy = date.today()
    alerta_limite = hoy + timedelta(days=30)

    # Productos activos
    c.execute("SELECT COUNT(*) FROM t_producto WHERE pro_estado = 'Activo'")
    total_productos = c.fetchone()[0]

    # Stock total
    c.execute("SELECT COALESCE(SUM(pro_cantidad_disponible), 0) FROM t_producto WHERE pro_estado = 'Activo'")
    stock_total = int(c.fetchone()[0])

    # Stock bajo
    c.execute("""
        SELECT COUNT(*) FROM t_producto
        WHERE pro_estado = 'Activo' AND pro_cantidad_disponible <= pro_stock_minimo
    """)
    stock_bajo = c.fetchone()[0]

    # Proveedores
    c.execute("SELECT COUNT(*) FROM t_proveedor")
    total_proveedores = c.fetchone()[0]

    # Pedidos activos y pendientes
    c.execute("""
        SELECT COUNT(*) FROM t_pedido
        WHERE ped_estado_entrega NOT IN ('Entregado', 'Anulado')
    """)
    pedidos_activos = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM t_pedido WHERE ped_estado_entrega = 'Pendiente'")
    pedidos_pendientes = c.fetchone()[0]

    # Compras pendientes y recibidas
    c.execute("SELECT COUNT(*) FROM t_compra WHERE com_estado = 'Pendiente'")
    compras_pendientes = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM t_compra WHERE com_estado = 'Recibida'")
    compras_recibidas = c.fetchone()[0]

    # Vencimientos críticos (≤30 días)
    c.execute("""
        SELECT COUNT(*)
        FROM t_lote l
        WHERE l.lot_estado = 'Activo'
          AND l.lot_fecha_vencimiento <= %s
          AND l.lot_fecha_vencimiento > CURDATE()
    """, (alerta_limite,))
    vencimientos_criticos = c.fetchone()[0]

    # Vencimientos próximos (31-60 días)
    c.execute("""
        SELECT COUNT(*)
        FROM t_lote l
        WHERE l.lot_estado = 'Activo'
          AND l.lot_fecha_vencimiento > %s
          AND l.lot_fecha_vencimiento <= DATE_ADD(CURDATE(), INTERVAL 60 DAY)
    """, (alerta_limite,))
    vencimientos_proximos = c.fetchone()[0]

    # Top 5 más vendidos
    c.execute("""
        SELECT pr.pro_id, pr.pro_nombre, COALESCE(SUM(dp.det_cantidad), 0) AS total_unidades
        FROM t_detalle_pedido dp
        JOIN t_pedido p ON p.ped_id = dp.det_ped_id_fk AND p.ped_estado_entrega != 'Anulado'
        JOIN t_producto pr ON pr.pro_id = dp.det_pro_id_fk
        GROUP BY pr.pro_id, pr.pro_nombre
        ORDER BY total_unidades DESC
        LIMIT 5
    """)
    top_vendidos = [{"pro_id": r[0], "nombre": r[1], "total_vendido": int(r[2])} for r in c.fetchall()]

    # Últimos 5 movimientos
    c.execute("""
        SELECT mon_id, mon_pro_id_fk, mon_tipo, mon_cantidad, mon_fecha
        FROM t_monitoria
        ORDER BY mon_fecha DESC, mon_id DESC
        LIMIT 5
    """)
    ultimos_movimientos = [{
        "id": r[0], "producto_id": r[1], "tipo": r[2],
        "cantidad": r[3], "fecha": str(r[4]) if r[4] else None
    } for r in c.fetchall()]

    # Alertas pendientes
    c.execute("SELECT COUNT(*) FROM t_alerta_vencimiento WHERE alv_estado = 'Pendiente'")
    alertas_pendientes = c.fetchone()[0]

    c.close()

    return jsonify({
        "productos": {"total": total_productos, "stock_total": stock_total, "stock_bajo": stock_bajo},
        "proveedores": {"total": total_proveedores},
        "pedidos": {"activos": pedidos_activos, "pendientes": pedidos_pendientes},
        "compras": {"pendientes": compras_pendientes, "recibidas": compras_recibidas},
        "vencimientos": {"criticos": vencimientos_criticos, "proximos": vencimientos_proximos},
        "top_vendidos": top_vendidos,
        "ultimos_movimientos": ultimos_movimientos,
        "alertas_pendientes": alertas_pendientes
    }), 200


@publico_bp.route('/confirmar-entrega/<token>', methods=['GET', 'POST'])
def confirmar_entrega(token):
    return cnconfirmarentrega(token)


@publico_bp.route('/public-url')
def public_url():
    """Devuelve la URL pública actual (ngrok si está disponible, localhost si no)."""
    from utils.ngrok_manager import obtener_url_publica
    return jsonify({"url": obtener_url_publica()}), 200


@publico_bp.route('/respaldar')
@token_requerido
def respaldar_bd():
    """Descarga un backup manual de la base de datos (solo Admin)."""
    if g.usuario_actual.get('rol') != 'Administrador':
        return jsonify({"error": "Se requiere rol de Administrador"}), 403

    try:
        db_host = current_app.config.get('MYSQL_HOST', 'localhost')
        db_port = str(current_app.config.get('MYSQL_PORT', 3306))
        db_user = current_app.config.get('MYSQL_USER', 'root')
        db_pass = current_app.config.get('MYSQL_PASSWORD', '')
        db_name = current_app.config.get('MYSQL_DB', 'db_drogueria_sandiego')

        fd, tmppath = tempfile.mkstemp(suffix='.sql', prefix='backup_manual_')
        os.close(fd)

        mysqldump_path = os.getenv('MYSQLDUMP_PATH', 'mysqldump')
        cmd = [mysqldump_path, f'--host={db_host}', f'--port={db_port}', f'--user={db_user}']
        if db_pass:
            cmd.append(f'--password={db_pass}')
        cmd.extend(['--single-transaction', '--routines', '--triggers', '--events', db_name])

        with open(tmppath, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, timeout=300)

        if result.returncode != 0:
            os.unlink(tmppath)
            return jsonify({"error": "Error al generar backup", "detalle": result.stderr.strip()}), 500

        from datetime import datetime
        download_name = f"backup_{db_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        return send_file(
            tmppath, mimetype='application/sql', as_attachment=True,
            download_name=download_name
        )
    except FileNotFoundError:
        return jsonify({"error": "mysqldump no encontrado. Configura MYSQLDUMP_PATH en .env"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
