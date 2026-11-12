SELECT id,titular,saldo FROM cuentas ORDER BY id;
SELECT SUM(saldo) AS saldo_total FROM cuentas;
SELECT COUNT(*) AS transferencias,COUNT(DISTINCT id) AS movimientos_unicos FROM movimientos;
