from flask import current_app
from models.mas_vendidos_model import mas_vendidos

def listarMasVendidos():
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT pro_id, pro_nombre, total_unidades_vendidas FROM v_mas_vendidos ORDER BY total_unidades_vendidas DESC")
    datos = c.fetchall()
    c.close()
    lista = []
    for p in datos:
        lista.append(mas_vendidos(p[0], p[1], p[2]).todic())
    return lista