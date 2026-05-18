-- Migración: agregar columnas de comprobante de pago a t_compra
-- Ejecutar contra la base de datos db_drogueria_sandiego

USE `db_drogueria_sandiego`;

ALTER TABLE `t_compra`
  ADD COLUMN `com_comprobante` LONGBLOB DEFAULT NULL COMMENT 'PDF o imagen del comprobante de pago',
  ADD COLUMN `com_comprobante_tipo` VARCHAR(50) DEFAULT NULL COMMENT 'MIME type del comprobante (ej: application/pdf, image/png)';
