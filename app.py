import os
import sys
import traceback
import socket
from flask import Flask, jsonify
from flask_mysqldb import MySQL
from routers import cargarruta
from config import config

app = Flask(__name__)
app.config.from_object(config)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# ── CORS: permitir peticiones desde cualquier origen ──
# Nota: se usa @app.after_request en lugar de CORS(app) porque
# es más robusto con blueprints y rutas registradas dinámicamente.

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

# ── Manejador global de errores: siempre devuelve JSON con CORS ──
@app.errorhandler(Exception)
def handle_exception(error):
    print(f"\n{'='*60}")
    print(f"  ❌ ERROR 500 — {type(error).__name__}")
    print(f"{'='*60}")
    traceback.print_exc()
    print(f"{'='*60}\n")
    response = jsonify({
        "error": "Error interno del servidor",
        "detalle": str(error)
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
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
        print("  ✅ Conexión a MySQL establecida correctamente")
    except Exception as e:
        print(f"\n  ❌ ERROR DE CONEXIÓN A MYSQL: {e}")
        print(f"     Revisa las credenciales en Backend/.env\n")

cargarruta(app)

if __name__ == '__main__':
    # 1. Leer puerto de variable de entorno PORT (si existe)
    # 2. Si no, usar 5000 como preferido
    # 3. Si el puerto está ocupado, usar uno libre
    preferred = int(os.getenv('PORT', 5000))
    port = find_free_port(preferred)

    print(f"\n{'='*50}")
    print(f"  🚀 Backend corriendo en:  http://localhost:{port}")
    print(f"  📡 Puerto original solicitado: {preferred}")
    if port != preferred:
        print(f"  ⚠️  El puerto {preferred} estaba ocupado — se asignó el {port}")
    print(f"{'='*50}\n")

    app.run(debug=True, port=port, host='0.0.0.0')