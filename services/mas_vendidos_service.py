from flask import current_app
from models.mas_vendidos_model import mas_vendidos

def listarMasVendidos():
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT * FROM v_mas_vendidos")
    datos = c.fetchall()
    c.close()
    lista = []
    for p in datos:
        # asumiendo 3 columnas; ajustar si son más
        lista.append(mas_vendidos(p[0], p[1], p[2]).todic())
    return lista