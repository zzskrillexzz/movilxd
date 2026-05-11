from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from routers import cargarruta
from config import config

app = Flask(__name__)
app.config.from_object(config)

# ── CORS: permitir peticiones desde cualquier origen ──
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

mysql = MySQL(app)
app.mysql = mysql
cargarruta(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')