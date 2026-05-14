class mas_vendidos:
    def __init__(self, pro_id, pro_nombre, total_vendido):
        self.pro_id = pro_id
        self.pro_nombre = pro_nombre
        self.total_vendido = total_vendido

    def todic(self):
        return {
            "producto_id": self.pro_id,
            "nombre": self.pro_nombre,
            "total_vendido": self.total_vendido
        }

    @staticmethod
    def get_all(mysql):
        cur = mysql.connection.cursor()
        cur.execute("SELECT pro_id, pro_nombre, total_unidades_vendidas FROM v_mas_vendidos ORDER BY total_unidades_vendidas DESC")
        rows = cur.fetchall()
        cur.close()
        
        resultados = []
        for row in rows:
            item = mas_vendidos(
                pro_id=row[0],
                pro_nombre=row[1],
                total_vendido=row[2]
            )
            resultados.append(item.todic())
        return resultados