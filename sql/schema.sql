CREATE DATABASE IF NOT EXISTS banco;
USE banco;
CREATE TABLE IF NOT EXISTS cuentas (
  id INT PRIMARY KEY,
  titular VARCHAR(100) NOT NULL,
  saldo DECIMAL(12,2) NOT NULL,
  CHECK (saldo >= 0)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS movimientos (
  id CHAR(36) PRIMARY KEY,
  origen INT NOT NULL,
  destino INT NOT NULL,
  importe DECIMAL(12,2) NOT NULL,
  confirmado_en TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  FOREIGN KEY (origen) REFERENCES cuentas(id),
  FOREIGN KEY (destino) REFERENCES cuentas(id),
  CHECK (importe > 0),
  CHECK (origen <> destino)
) ENGINE=InnoDB;
