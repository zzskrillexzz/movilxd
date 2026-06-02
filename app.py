import os
import sys
import socket
from flask import Flask, jsonify, send_from_directory
from flask_mysqldb import MySQL
from routers import cargarruta
from config import config
from utils.logger import get_logger

# ── Forzar salida UTF-8 en consola Windows ──
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

log = get_logger(__name__)

app = Flask(__name__)
app.config.from_object(config)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# ── BUG-007: Validar SECRET_KEY al arranque ──
_secret = app.config.get('SECRET_KEY')
if not _secret:
    raise RuntimeError(
        "SECRET_KEY no está configurada. "
        "Revisa Backend/.env — debe contener SECRET_KEY=..."
    )
if len(str(_secret)) < 16:
    raise RuntimeError(
        f"SECRET_KEY demasiado corta ({len(str(_secret))} chars). "
        "Mínimo recomendado: 32 caracteres."
    )

# ── CORS: permitir peticiones desde cualquier origen ──
# Nota: se usa @app.after_request en lugar de CORS(app) porque
# es más robusto con blueprints y rutas registradas dinámicamente.

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    # Seguridad básica en headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

# ── Manejador global de errores: siempre devuelve JSON con CORS ──
@app.errorhandler(Exception)
def handle_exception(error):
    log.error("ERROR 500 — %s: %s", type(error).__name__, str(error), exc_info=True)
    
    # BUG-012: No exponer stack traces en producción
    es_produccion = os.getenv('FLASK_ENV', 'development') == 'production'
    response = jsonify({
        "error": "Error interno del servidor",
        "detalle": str(error) if not es_produccion else "Ocurrió un error inesperado. Contacta al administrador."
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.status_code = 500
    return response


def find_free_port(preferred_port):
    """
    Intenta usar el puerto preferido; si está ocupado,
    deja que el SO asigne uno libre automáticamente.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('0.0.0.0', preferred_port))
        return preferred_port
    except OSError:
        sock.bind(('0.0.0.0', 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


mysql = MySQL(app)
app.mysql = mysql

# ── Verificar conexión a MySQL al arrancar ──
with app.app_context():
    try:
        c = mysql.connection.cursor()
        c.execute("SELECT 1")
        c.close()
        log.info("Conexion a MySQL establecida correctamente")
    except Exception as e:
        log.critical("ERROR DE CONEXION A MYSQL: %s — Revisa las credenciales en Backend/.env", e)

cargarruta(app)

# ── Servir el frontend build desde Flask ──
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Frontend', 'dist')
if os.path.isdir(FRONTEND_DIST):
    @app.route('/assets/<path:filename>')
    def frontend_assets(filename):
        return send_from_directory(os.path.join(FRONTEND_DIST, 'assets'), filename)

    @app.route('/<path:path>')
    def frontend_fallback(path):
        filepath = os.path.join(FRONTEND_DIST, path)
        if os.path.isfile(filepath):
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, 'index.html')

    log.info("Sirviendo frontend desde: %s", FRONTEND_DIST)
else:
    log.warning("Frontend build no encontrado en %s — ejecuta: cd Frontend && pnpm build", FRONTEND_DIST)

if __name__ == '__main__':
    preferred = int(os.getenv('PORT', 5000))
    port = find_free_port(preferred)

    log.info("=" * 50)
    log.info("Backend corriendo en: http://localhost:%s", port)
    log.info("Puerto original solicitado: %s", preferred)
    if port != preferred:
        log.warning("El puerto %s estaba ocupado — se asigno el %s", preferred, port)
    log.info("=" * 50)

    app.run(debug=True, port=port, host='0.0.0.0')
