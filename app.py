from flask import Flask
from flask_mysqldb import MySQL
from routers import cargarruta
from config import config

app = Flask(__name__)
app.config.from_object(config)

mysql = MySQL(app)
app.mysql = mysql
cargarruta(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')