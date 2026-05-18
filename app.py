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
    response = jsonify({
        "error": "Error interno del servidor",
        "detalle": str(error)
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.status_code = 500
    return response

mysql = MySQL(app)
app.mysql = mysql
cargarruta(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')