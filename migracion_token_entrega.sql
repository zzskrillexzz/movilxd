-- Migración: Agregar columna para token único de confirmación de entrega
-- Este token se genera cuando el pedido pasa a estado "En camino"
-- y se usa en el código QR para que el repartidor confirme la entrega

ALTER TABLE `t_pedido`
  ADD COLUMN IF NOT EXISTS `ped_token_entrega` VARCHAR(64) DEFAULT NULL COMMENT 'Token único para confirmación de entrega vía QR' AFTER `ped_estado_pago`;
