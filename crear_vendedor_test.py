import bcrypt
import MySQLdb

salt = bcrypt.gensalt()
pwd_hash = bcrypt.hashpw(b'vendedor123', salt).decode()

conn = MySQLdb.connect(host='localhost', user='root', port=3307, db='db_drogueria_sandiego')
c = conn.cursor()
try:
    c.execute("INSERT INTO t_usuario (usu_id, usu_nombre, usu_correo, usu_contrasena, usu_rol_id_fk, usu_estado) VALUES (%s, %s, %s, %s, %s, %s)",
              ('USU201', 'Vendedor Test', 'vendedor@test.com', pwd_hash, 'ROL002', 1))
    conn.commit()
    print("Usuario vendedor creado: vendedor@test.com / vendedor123")
except Exception as e:
    print(f"Error: {e}")
    # Try updating if exists
    try:
        c.execute("UPDATE t_usuario SET usu_contrasena=%s, usu_estado=1 WHERE usu_correo=%s", (pwd_hash, 'vendedor@test.com'))
        conn.commit()
        print("Usuario vendedor actualizado")
    except:
        print("Fallo total")
finally:
    c.close()
    conn.close()
