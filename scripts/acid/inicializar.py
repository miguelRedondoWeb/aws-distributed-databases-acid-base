from pathlib import Path
from common import connection

sql = (Path(__file__).resolve().parents[2] / "sql" / "schema.sql").read_text(encoding="utf-8")
conn = connection()
try:
    with conn.cursor() as cur:
        for stmt in sql.split(";"):
            if stmt.strip():
                cur.execute(stmt)
        cur.execute("SELECT COUNT(*) FROM movimientos")
        if cur.fetchone()[0]:
            raise RuntimeError("Ya existen transferencias: no reinicializar la práctica")
        cur.execute("DELETE FROM cuentas")
        cur.executemany("INSERT INTO cuentas(id,titular,saldo) VALUES (%s,%s,2000)",
             [(1,"Ana"),(2,"Luis"),(3,"Marta"),(4,"Carlos"),(5,"Elena")])
    conn.commit()
    print("5 cuentas inicializadas. Saldo total: 10.000 EUR")
finally:
    conn.close()
