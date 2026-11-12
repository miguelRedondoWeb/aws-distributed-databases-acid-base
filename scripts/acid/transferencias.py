import csv
import os
import random
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from common import connection

RESULTS = Path(__file__).resolve().parents[2] / "results"
RESULTS.mkdir(exist_ok=True)
LOG = RESULTS / "transferencias.csv"
newfile = not LOG.exists()
file = LOG.open("a", encoding="utf-8", newline="", buffering=1)
writer = csv.writer(file)
if newfile:
    writer.writerow(["id","utc","origen","destino","importe","commit_ms","estado"])
    file.flush(); os.fsync(file.fileno())
print("Transferencias continuas. Forzar failover en otra terminal. CTRL+C para terminar.")
print("CSV:", LOG)
conn = None
ok = 0
fails = 0
try:
    while True:
        a,b = random.sample(range(1,6),2)
        amount = Decimal(random.choice([1,2,5,10,20]))
        txid = str(uuid.uuid4())
        try:
            if conn is None:
                conn = connection()
            t0=time.perf_counter()
            with conn.cursor() as cur:
                cur.execute("SELECT saldo FROM cuentas WHERE id=%s FOR UPDATE", (a,))
                src = cur.fetchone()
                if src is None or src[0] < amount:
                    conn.rollback()
                    continue
                cur.execute("UPDATE cuentas SET saldo=saldo-%s WHERE id=%s", (amount,a))
                cur.execute("UPDATE cuentas SET saldo=saldo+%s WHERE id=%s", (amount,b))
                cur.execute("INSERT INTO movimientos(id,origen,destino,importe) VALUES (%s,%s,%s,%s)", (txid,a,b,amount))
            conn.commit()
            ms=round((time.perf_counter()-t0)*1000,2)
            writer.writerow([txid,datetime.now(timezone.utc).isoformat(),a,b,str(amount),ms,"CONFIRMADA"])
            file.flush();os.fsync(file.fileno())
            ok += 1
            print(f"OK #{ok} {txid[:8]} {a}->{b} EUR {amount} COMMIT {ms} ms",flush=True)
        except Exception as e:
            fails += 1
            print(f"ERROR #{fails} {datetime.now(timezone.utc).isoformat()} {type(e).__name__}: {e}",flush=True)
            if conn:
                try: conn.close()
                except Exception: pass
            conn=None
            # Important: failure after sending COMMIT can be ambiguous.
            # Never retry the same transaction ID automatically.
        time.sleep(0.5)
except KeyboardInterrupt:
    print(f"FINAL: confirmadas={ok} errores={fails}")
finally:
    if conn:
        try: conn.close()
        except Exception: pass
    file.close()
