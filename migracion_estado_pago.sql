-- Migración: agregar columna ped_estado_pago a t_pedido
-- Ejecutar contra la base de datos db_drogueria_sandiego

USE `db_drogueria_sandiego`;

ALTER TABLE `t_pedido`
  ADD COLUMN `ped_estado_pago` VARCHAR(20) DEFAULT 'Pendiente' COMMENT 'Estado del pago: Pendiente / Verificado / Rechazado' AFTER `ped_estado_entrega`;
