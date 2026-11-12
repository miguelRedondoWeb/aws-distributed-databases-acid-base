import csv
import statistics
from pathlib import Path
from common import connection

root=Path(__file__).resolve().parents[2]
log=root/"results"/"transferencias.csv"
assert log.exists(), f"No existe {log}"
with log.open(encoding="utf-8",newline="") as f:
    confirmed=[r for r in csv.DictReader(f) if r["estado"]=="CONFIRMADA"]
ids=[r["id"] for r in confirmed]
conn=connection()
try:
    with conn.cursor() as cur:
        cur.execute("SELECT id,titular,saldo FROM cuentas ORDER BY id")
        accounts=cur.fetchall()
        cur.execute("SELECT id FROM movimientos")
        db_ids=[r[0] for r in cur.fetchall()]
finally:
    conn.close()
missing=set(ids)-set(db_ids)
print("CUENTAS:",accounts)
print("TOTAL:",sum(r[2] for r in accounts),"EUR")
print("Confirmadas al cliente:",len(ids))
print("Movimientos en BD:",len(db_ids))
print("Confirmadas perdidas:",len(missing),missing)
print("Duplicados BD:",len(db_ids)-len(set(db_ids)))
print("Latencia COMMIT media (ms):",round(statistics.mean(float(r["commit_ms"]) for r in confirmed),2) if confirmed else "Sin datos")
if len(ids)!=len(set(ids)) or missing or len(db_ids)!=len(set(db_ids)) or sum(r[2] for r in accounts)!=10000:
    raise SystemExit("VERIFICACION NO SUPERADA")
print("VERIFICACION ACID SUPERADA. La medida RTO requiere correlacionar el corte y la recuperacion en el log.")
