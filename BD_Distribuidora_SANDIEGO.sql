/*
SQLyog Trial v13.1.9 (64 bit)
MySQL - 10.4.32-MariaDB : Database - db_drogueria_sandiego
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`db_drogueria_sandiego` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `db_drogueria_sandiego`;

/*Table structure for table `t_alerta_vencimiento` */

DROP TABLE IF EXISTS `t_alerta_vencimiento`;

CREATE TABLE `t_alerta_vencimiento` (
  `alv_id` varchar(20) NOT NULL COMMENT 'ID de la alerta',
  `alv_pro_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del producto',
  `alv_lot_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del lote próximo a vencer',
  `alv_fecha_generacion` date DEFAULT NULL COMMENT 'Fecha en que se generó la alerta',
  `alv_fecha_vencimiento` date DEFAULT NULL COMMENT 'Fecha de vencimiento del lote',
  `alv_dias_restantes` int(11) DEFAULT NULL COMMENT 'Días restantes al momento de generar la alerta',
  `alv_estado` varchar(20) DEFAULT 'Pendiente' COMMENT 'Estado: Pendiente / Gestionada / Ignorada',
  `alv_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del usuario que gestionó la alerta',
  PRIMARY KEY (`alv_id`),
  KEY `alv_pro_id_fk` (`alv_pro_id_fk`),
  KEY `alv_lot_id_fk` (`alv_lot_id_fk`),
  KEY `alv_usu_id_fk` (`alv_usu_id_fk`),
  CONSTRAINT `alerta_ibfk_1` FOREIGN KEY (`alv_pro_id_fk`) REFERENCES `t_producto` (`pro_id`),
  CONSTRAINT `alerta_ibfk_2` FOREIGN KEY (`alv_lot_id_fk`) REFERENCES `t_lote` (`lot_id`),
  CONSTRAINT `alerta_ibfk_3` FOREIGN KEY (`alv_usu_id_fk`) REFERENCES `t_usuario` (`usu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_alerta_vencimiento` */

insert  into `t_alerta_vencimiento`(`alv_id`,`alv_pro_id_fk`,`alv_lot_id_fk`,`alv_fecha_generacion`,`alv_fecha_vencimiento`,`alv_dias_restantes`,`alv_estado`,`alv_usu_id_fk`) values 
('ALV001','PRO002','LOT002','2025-03-19','2026-06-30',468,'Pendiente',NULL),
('ALV050','PRO050','LOT050','2026-04-09','2027-06-30',447,'Pendiente',NULL),
('ALV051','PRO051','LOT051','2026-04-09','2027-09-15',524,'Pendiente',NULL),
('ALV052','PRO052','LOT052','2026-04-09','2028-01-20',651,'Gestionada',NULL),
('ALV099','PRO001','LOT001','2026-04-09','2026-08-31',144,'Pendiente',NULL);

/*Table structure for table `t_anulacion_venta` */

DROP TABLE IF EXISTS `t_anulacion_venta`;

CREATE TABLE `t_anulacion_venta` (
  `anu_id` varchar(20) NOT NULL COMMENT 'ID de la anulación',
  `anu_fac_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID de la factura anulada',
  `anu_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del usuario que anuló',
  `anu_fecha` datetime DEFAULT NULL COMMENT 'Fecha y hora de la anulación',
  `anu_motivo` varchar(255) DEFAULT NULL COMMENT 'Motivo de la anulación',
  PRIMARY KEY (`anu_id`),
  KEY `anu_fac_id_fk` (`anu_fac_id_fk`),
  KEY `anu_usu_id_fk` (`anu_usu_id_fk`),
  CONSTRAINT `anulacion_ibfk_1` FOREIGN KEY (`anu_fac_id_fk`) REFERENCES `t_factura` (`fac_id`),
  CONSTRAINT `anulacion_ibfk_2` FOREIGN KEY (`anu_usu_id_fk`) REFERENCES `t_usuario` (`usu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_anulacion_venta` */

insert  into `t_anulacion_venta`(`anu_id`,`anu_fac_id_fk`,`anu_usu_id_fk`,`anu_fecha`,`anu_motivo`) values 
('ANU050','PED050','USU051','2026-04-09 16:00:00','Cliente solicito devolucion'),
('ANU051','PED051','USU051','2026-04-09 17:00:00','Error en facturacion'),
('ANU052','PED052','USU052','2026-04-09 18:00:00','Producto defectuoso'),
('ANU099','PED001','USU001','2026-04-09 12:00:00','Test anulacion');

/*Table structure for table `t_cliente` */

DROP TABLE IF EXISTS `t_cliente`;

CREATE TABLE `t_cliente` (
  `cli_id` bigint(20) NOT NULL COMMENT 'Número de documento del cliente',
  `cli_tipo_documento` varchar(10) DEFAULT 'CC' COMMENT 'Tipo: CC / NIT / CE / TI',
  `cli_nombre` varchar(50) DEFAULT NULL COMMENT 'Nombre del cliente',
  `cli_apellido` varchar(50) DEFAULT NULL COMMENT 'Apellido del cliente',
  `cli_telefono` varchar(20) DEFAULT NULL COMMENT 'Teléfono del cliente',
  `cli_direccion` varchar(100) DEFAULT NULL COMMENT 'Dirección del cliente',
  `cli_correo` varchar(100) DEFAULT NULL COMMENT 'Correo del cliente',
  PRIMARY KEY (`cli_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_cliente` */

insert  into `t_cliente`(`cli_id`,`cli_tipo_documento`,`cli_nombre`,`cli_apellido`,`cli_telefono`,`cli_direccion`,`cli_correo`) values 
(1023456789,'CC','Carlos','Gomez','3157894561','Cl 80 #20-35','cgomez@hotmail.com'),
(1065432198,'CC','Maria','Salcedo','3143216547','Cl 45 #8-15','msalcedo@gmail.com'),
(1076543219,'CC','Jhon','Rios','3209876543','Cra 7 #12-50','jhonrios@gmail.com'),
(1087654321,'CC','Ana','Torres','3012345678','Av 68 #55-20','ana.torres@yahoo.com'),
(1098765432,'CC','Laura','Martinez','3104567890','Cra 15 #42-10','l.martinez@gmail.com'),
(900123456,'NIT','Farmacia','El Descuento SAS','6014567890','Av 68 #23-45 Cali','farmacia.descuento@empresa.co'),
(9999999999,'CC','Test','Usuario','3001234567','Calle 1 #2-3','test@test.com');

/*Table structure for table `t_compra` */

DROP TABLE IF EXISTS `t_compra`;

CREATE TABLE `t_compra` (
  `com_id` varchar(20) NOT NULL COMMENT 'ID de la compra',
  `com_fecha` date DEFAULT NULL COMMENT 'Fecha de la compra',
  `com_prov_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del proveedor',
  `com_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del usuario que registró la compra',
  `com_total` decimal(12,2) DEFAULT NULL COMMENT 'Total de la compra',
  `com_estado` varchar(20) DEFAULT 'Recibida' COMMENT 'Estado: Pendiente / Recibida / Cancelada',
  `com_observacion` varchar(255) DEFAULT NULL COMMENT 'Observaciones de la compra',
  PRIMARY KEY (`com_id`),
  KEY `com_prov_id_fk` (`com_prov_id_fk`),
  KEY `com_usu_id_fk` (`com_usu_id_fk`),
  CONSTRAINT `compra_ibfk_1` FOREIGN KEY (`com_prov_id_fk`) REFERENCES `t_proveedor` (`prov_id`),
  CONSTRAINT `compra_ibfk_2` FOREIGN KEY (`com_usu_id_fk`) REFERENCES `t_usuario` (`usu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_compra` */

insert  into `t_compra`(`com_id`,`com_fecha`,`com_prov_id_fk`,`com_usu_id_fk`,`com_total`,`com_estado`,`com_observacion`) values 
('COM001','2025-03-10','PROV002','USU004',85000.00,'Recibida','Compra mensual Acetaminofen'),
('COM002','2025-03-12','PROV003','USU004',49000.00,'Recibida','Reposición Loratadina'),
('COM050','2026-04-09','PROV050','USU051',850000.00,'Recibida','Compra de Ibuprofeno'),
('COM051','2026-04-09','PROV051','USU051',450000.00,'Pendiente','Compra de Amoxicilina'),
('COM052','2026-04-09','PROV052','USU052',260000.00,'Recibida','Compra de Loratadina');

/*Table structure for table `t_detalle_compra` */

DROP TABLE IF EXISTS `t_detalle_compra`;

CREATE TABLE `t_detalle_compra` (
  `dco_id` varchar(20) NOT NULL COMMENT 'ID del detalle de compra',
  `dco_com_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID de la compra',
  `dco_pro_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del producto comprado',
  `dco_lot_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del lote recibido',
  `dco_cantidad` int(11) DEFAULT NULL COMMENT 'Cantidad comprada',
  `dco_precio_compra` decimal(12,2) DEFAULT NULL COMMENT 'Precio de compra unitario',
  `dco_subtotal` decimal(12,2) DEFAULT NULL COMMENT 'Subtotal (cantidad × precio_compra)',
  PRIMARY KEY (`dco_id`),
  KEY `dco_com_id_fk` (`dco_com_id_fk`),
  KEY `dco_pro_id_fk` (`dco_pro_id_fk`),
  KEY `dco_lot_id_fk` (`dco_lot_id_fk`),
  CONSTRAINT `det_compra_ibfk_1` FOREIGN KEY (`dco_com_id_fk`) REFERENCES `t_compra` (`com_id`),
  CONSTRAINT `det_compra_ibfk_2` FOREIGN KEY (`dco_pro_id_fk`) REFERENCES `t_producto` (`pro_id`),
  CONSTRAINT `det_compra_ibfk_3` FOREIGN KEY (`dco_lot_id_fk`) REFERENCES `t_lote` (`lot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_detalle_compra` */

insert  into `t_detalle_compra`(`dco_id`,`dco_com_id_fk`,`dco_pro_id_fk`,`dco_lot_id_fk`,`dco_cantidad`,`dco_precio_compra`,`dco_subtotal`) values 
('DCO001','COM001','PRO001','LOT001',100,850.00,85000.00),
('DCO002','COM002','PRO003','LOT003',50,980.00,49000.00),
('DCO050','COM050','PRO050','LOT050',100,8500.00,850000.00),
('DCO051','COM051','PRO051','LOT051',30,15000.00,450000.00),
('DCO052','COM052','PRO052','LOT052',50,5200.00,260000.00);

/*Table structure for table `t_detalle_pedido` */

DROP TABLE IF EXISTS `t_detalle_pedido`;

CREATE TABLE `t_detalle_pedido` (
  `det_id` varchar(20) NOT NULL COMMENT 'ID del detalle',
  `det_ped_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del pedido al que pertenece',
  `det_pro_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del producto vendido',
  `det_cantidad` int(11) DEFAULT NULL COMMENT 'Cantidad de unidades',
  `det_precio_unitario` decimal(12,2) DEFAULT NULL COMMENT 'Precio unitario al momento de la venta',
  `det_subtotal` decimal(12,2) DEFAULT NULL COMMENT 'Subtotal (cantidad × precio_unitario)',
  PRIMARY KEY (`det_id`),
  KEY `det_ped_id_fk` (`det_ped_id_fk`),
  KEY `det_pro_id_fk` (`det_pro_id_fk`),
  CONSTRAINT `detalle_ibfk_1` FOREIGN KEY (`det_ped_id_fk`) REFERENCES `t_pedido` (`ped_id`),
  CONSTRAINT `detalle_ibfk_2` FOREIGN KEY (`det_pro_id_fk`) REFERENCES `t_producto` (`pro_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_detalle_pedido` */

insert  into `t_detalle_pedido`(`det_id`,`det_ped_id_fk`,`det_pro_id_fk`,`det_cantidad`,`det_precio_unitario`,`det_subtotal`) values 
('DET001','PED001','PRO001',5,850.00,4250.00),
('DET002','PED002','PRO002',3,1200.00,3600.00),
('DET003','PED003','PRO003',4,980.00,3920.00),
('DET004','PED004','PRO004',2,3500.00,7000.00),
('DET005','PED005','PRO005',1,4200.00,4200.00),
('DET050','PED050','PRO050',2,8500.00,17000.00),
('DET051','PED051','PRO051',2,15000.00,30000.00),
('DET052','PED052','PRO052',1,5200.00,5200.00);

/*Table structure for table `t_factura` */

DROP TABLE IF EXISTS `t_factura`;

CREATE TABLE `t_factura` (
  `fac_id` varchar(20) NOT NULL COMMENT 'ID de la factura (coincide con ped_id)',
  `fac_fecha_emision` date DEFAULT NULL COMMENT 'Fecha de emisión',
  `fac_email_enviado` tinyint(1) DEFAULT NULL COMMENT '1=Enviado / 0=No enviado',
  `fac_forma_pago` varchar(50) DEFAULT NULL COMMENT 'Forma de pago',
  `fac_cuenta_bancaria` varchar(50) DEFAULT NULL COMMENT 'Cuenta bancaria para transferencia',
  `fac_total` decimal(12,2) DEFAULT NULL COMMENT 'Total de la factura',
  `fac_estado` varchar(20) DEFAULT 'Vigente' COMMENT 'Estado: Vigente / Anulada',
  `fac_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del usuario que generó la factura',
  PRIMARY KEY (`fac_id`),
  KEY `fac_usu_id_fk` (`fac_usu_id_fk`),
  CONSTRAINT `factura_ibfk_1` FOREIGN KEY (`fac_id`) REFERENCES `t_pedido` (`ped_id`),
  CONSTRAINT `factura_ibfk_2` FOREIGN KEY (`fac_usu_id_fk`) REFERENCES `t_usuario` (`usu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_factura` */

insert  into `t_factura`(`fac_id`,`fac_fecha_emision`,`fac_email_enviado`,`fac_forma_pago`,`fac_total`,`fac_estado`,`fac_usu_id_fk`) values 
('PED001','2025-03-15',1,'Efectivo',8450.00,'Vigente','USU002'),
('PED002','2025-03-16',1,'Tarjeta',12700.00,'Vigente','USU003'),
('PED003','2025-03-17',0,'Nequi',5880.00,'Vigente','USU002'),
('PED004','2025-03-18',0,'Efectivo',4200.00,'Vigente','USU003'),
('PED005','2025-03-19',1,'Daviplata',9800.00,'Vigente','USU002'),
('PED050','2026-04-09',1,'Efectivo',17000.00,'Vigente','USU050'),
('PED051','2026-04-09',0,'Tarjeta',30000.00,'Vigente','USU051'),
('PED052','2026-04-09',1,'Transferencia',5200.00,'Vigente','USU052');

/*Table structure for table `t_inventario_movimiento` */

DROP TABLE IF EXISTS `t_inventario_movimiento`;

CREATE TABLE `t_inventario_movimiento` (
  `inm_id` varchar(20) NOT NULL COMMENT 'ID del movimiento',
  `inm_tipo_movimiento` varchar(20) DEFAULT NULL COMMENT 'Tipo: Entrada / Salida / Ajuste',
  `inm_pro_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del producto',
  `inm_lot_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del lote involucrado',
  `inm_cantidad` int(11) DEFAULT NULL COMMENT 'Cantidad del movimiento',
  `inm_fecha` date DEFAULT NULL COMMENT 'Fecha del movimiento',
  `inm_motivo` varchar(255) DEFAULT NULL COMMENT 'Motivo del movimiento',
  `inm_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del usuario responsable',
  PRIMARY KEY (`inm_id`),
  KEY `inm_pro_id_fk` (`inm_pro_id_fk`),
  KEY `inm_lot_id_fk` (`inm_lot_id_fk`),
  KEY `inm_usu_id_fk` (`inm_usu_id_fk`),
  CONSTRAINT `inventario_ibfk_1` FOREIGN KEY (`inm_pro_id_fk`) REFERENCES `t_producto` (`pro_id`),
  CONSTRAINT `inventario_ibfk_2` FOREIGN KEY (`inm_usu_id_fk`) REFERENCES `t_usuario` (`usu_id`),
  CONSTRAINT `inventario_ibfk_3` FOREIGN KEY (`inm_lot_id_fk`) REFERENCES `t_lote` (`lot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_inventario_movimiento` */

insert  into `t_inventario_movimiento`(`inm_id`,`inm_tipo_movimiento`,`inm_pro_id_fk`,`inm_lot_id_fk`,`inm_cantidad`,`inm_fecha`,`inm_motivo`,`inm_usu_id_fk`) values 
('INM001','Entrada','PRO001','LOT001',100,'2025-03-10','Compra proveedor COM001','USU004'),
('INM002','Salida','PRO001','LOT001',5,'2025-03-15','Venta PED001','USU002'),
('INM003','Salida','PRO002','LOT002',3,'2025-03-16','Venta PED002','USU003'),
('INM004','Entrada','PRO003','LOT003',50,'2025-03-12','Compra proveedor COM002','USU004'),
('INM005','Salida','PRO005','LOT005',1,'2025-03-18','Venta PED004','USU003'),
('INM050','Entrada','PRO050','LOT050',100,'2026-04-09','Compra COM050','USU051'),
('INM051','Entrada','PRO051','LOT051',150,'2026-04-09','Compra COM051','USU051'),
('INM052','Salida','PRO052','LOT052',10,'2026-04-09','Venta PED052','USU052'),
('INM053','Salida ','PRO052','LOT099',1,'2026-04-09','Venta PED052','USU052');

/*Table structure for table `t_lote` */

DROP TABLE IF EXISTS `t_lote`;

CREATE TABLE `t_lote` (
  `lot_id` varchar(20) NOT NULL COMMENT 'ID del lote',
  `lot_numero` varchar(50) DEFAULT NULL COMMENT 'Número de lote del fabricante',
  `lot_fecha_fabricacion` date DEFAULT NULL COMMENT 'Fecha de fabricación',
  `lot_fecha_vencimiento` date NOT NULL COMMENT 'Fecha de vencimiento del lote',
  `lot_cantidad_inicial` int(11) DEFAULT 0 COMMENT 'Cantidad recibida en este lote',
  `lot_cantidad_actual` int(11) DEFAULT 0 COMMENT 'Cantidad disponible en este lote',
  `lot_pro_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del producto al que pertenece este lote',
  `lot_prov_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del proveedor que suministró el lote',
  `lot_estado` varchar(20) DEFAULT 'Activo' COMMENT 'Estado: Activo / Agotado / Vencido / Cuarentena',
  PRIMARY KEY (`lot_id`),
  KEY `lot_pro_id_fk` (`lot_pro_id_fk`),
  KEY `lot_prov_id_fk` (`lot_prov_id_fk`),
  CONSTRAINT `lote_ibfk_1` FOREIGN KEY (`lot_pro_id_fk`) REFERENCES `t_producto` (`pro_id`),
  CONSTRAINT `lote_ibfk_2` FOREIGN KEY (`lot_prov_id_fk`) REFERENCES `t_proveedor` (`prov_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_lote` */

insert  into `t_lote`(`lot_id`,`lot_numero`,`lot_fecha_fabricacion`,`lot_fecha_vencimiento`,`lot_cantidad_inicial`,`lot_cantidad_actual`,`lot_pro_id_fk`,`lot_prov_id_fk`,`lot_estado`) values 
('LOT001','LT-ACE-2025-001','2025-01-10','2026-08-31',200,195,'PRO001','PROV002','Activo'),
('LOT002','LT-IBU-2025-001','2025-02-05','2026-06-30',150,147,'PRO002','PROV001','Activo'),
('LOT003','LT-LOR-2025-001','2025-01-20','2027-01-31',80,80,'PRO003','PROV003','Activo'),
('LOT004','LT-SUE-2025-001','2025-03-01','2026-12-15',60,60,'PRO004','PROV004','Activo'),
('LOT005','LT-ALC-2025-001','2025-02-15','2027-05-20',45,44,'PRO005','PROV005','Activo'),
('LOT050','LT-IBU-2026-050','2026-01-15','2027-06-30',100,100,'PRO050','PROV050','Activo'),
('LOT051','LT-AMO-2026-051','2026-02-01','2027-09-15',150,150,'PRO051','PROV051','Activo'),
('LOT052','LT-LOR-2026-052','2026-03-10','2028-01-20',300,300,'PRO052','PROV052','Activo'),
('LOT099','LT-TEST-2026','2026-01-01','2027-06-30',100,100,'PRO001','PROV002','Activo');

/*Table structure for table `t_monitoria` */

DROP TABLE IF EXISTS `t_monitoria`;

CREATE TABLE `t_monitoria` (
  `mon_id` varchar(20) NOT NULL COMMENT 'ID del registro de monitoria',
  `mon_pro_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del producto',
  `mon_lot_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del lote',
  `mon_inm_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del movimiento que generó este registro',
  `mon_fecha` date DEFAULT NULL COMMENT 'Fecha del movimiento',
  `mon_tipo` varchar(20) DEFAULT NULL COMMENT 'Entrada / Salida / Ajuste',
  `mon_cantidad` int(11) DEFAULT NULL COMMENT 'Cantidad del movimiento',
  `mon_saldo_anterior` int(11) DEFAULT NULL COMMENT 'Stock antes del movimiento',
  `mon_saldo_actual` int(11) DEFAULT NULL COMMENT 'Stock después del movimiento',
  `mon_costo_unitario` decimal(12,2) DEFAULT NULL COMMENT 'Costo unitario del producto',
  `mon_costo_total` decimal(12,2) DEFAULT NULL COMMENT 'Costo total del movimiento',
  PRIMARY KEY (`mon_id`),
  KEY `mon_pro_id_fk` (`mon_pro_id_fk`),
  KEY `mon_lot_id_fk` (`mon_lot_id_fk`),
  KEY `mon_inm_id_fk` (`mon_inm_id_fk`),
  CONSTRAINT `monitoria_ibfk_1` FOREIGN KEY (`mon_pro_id_fk`) REFERENCES `t_producto` (`pro_id`),
  CONSTRAINT `monitoria_ibfk_2` FOREIGN KEY (`mon_lot_id_fk`) REFERENCES `t_lote` (`lot_id`),
  CONSTRAINT `monitoria_ibfk_3` FOREIGN KEY (`mon_inm_id_fk`) REFERENCES `t_inventario_movimiento` (`inm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Historial de monitoreo de inventario (antes kardex)';

/*Data for the table `t_monitoria` */

insert  into `t_monitoria`(`mon_id`,`mon_pro_id_fk`,`mon_lot_id_fk`,`mon_inm_id_fk`,`mon_fecha`,`mon_tipo`,`mon_cantidad`,`mon_saldo_anterior`,`mon_saldo_actual`,`mon_costo_unitario`,`mon_costo_total`) values 
('MON001','PRO001','LOT001','INM001','2025-03-10','Entrada',100,100,200,850.00,85000.00),
('MON002','PRO001','LOT001','INM002','2025-03-15','Salida',5,200,195,850.00,4250.00),
('MON003','PRO002','LOT002','INM003','2025-03-16','Salida',3,150,147,1200.00,3600.00),
('MON004','PRO003','LOT003','INM004','2025-03-12','Entrada',50,30,80,980.00,49000.00),
('MON005','PRO005','LOT005','INM005','2025-03-18','Salida',1,45,44,4200.00,4200.00),
('MON050','PRO050','LOT050','INM050','2026-04-09','Entrada',100,200,300,8500.00,850000.00),
('MON051','PRO051','LOT051','INM051','2026-04-09','Entrada',150,150,300,15000.00,2250000.00),
('MON052','PRO052','LOT052','INM052','2026-04-09','Salida',10,300,290,5200.00,52000.00);

/*Table structure for table `t_pedido` */

DROP TABLE IF EXISTS `t_pedido`;

CREATE TABLE `t_pedido` (
  `ped_id` varchar(20) NOT NULL COMMENT 'ID del pedido',
  `ped_fecha` date DEFAULT NULL COMMENT 'Fecha del pedido',
  `ped_metodo_pago` varchar(50) DEFAULT NULL COMMENT 'Método de pago',
  `ped_cuenta_bancaria` varchar(50) DEFAULT NULL COMMENT 'Cuenta bancaria para transferencia',
  `ped_estado_entrega` varchar(50) DEFAULT NULL COMMENT 'Estado: Entregado / En camino / No entregado / Anulado',
  `ped_estado_pago` varchar(20) DEFAULT 'Pendiente' COMMENT 'Estado del pago: Pendiente / Verificado / Rechazado',
  `ped_total` decimal(12,2) DEFAULT NULL COMMENT 'Total del pedido',
  `ped_cli_id_fk` bigint(20) DEFAULT NULL COMMENT 'ID del cliente',
  `ped_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del vendedor que registró el pedido',
  PRIMARY KEY (`ped_id`),
  KEY `ped_cli_id_fk` (`ped_cli_id_fk`),
  KEY `ped_usu_id_fk` (`ped_usu_id_fk`),
  CONSTRAINT `pedido_ibfk_1` FOREIGN KEY (`ped_cli_id_fk`) REFERENCES `t_cliente` (`cli_id`),
  CONSTRAINT `pedido_ibfk_2` FOREIGN KEY (`ped_usu_id_fk`) REFERENCES `t_usuario` (`usu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_pedido` */

insert  into `t_pedido`(`ped_id`,`ped_fecha`,`ped_metodo_pago`,`ped_estado_entrega`,`ped_total`,`ped_cli_id_fk`,`ped_usu_id_fk`) values 
('PED001','2025-03-15','Efectivo','Entregado',8450.00,1098765432,'USU002'),
('PED002','2025-03-16','Tarjeta','En camino',12700.00,1023456789,'USU003'),
('PED003','2025-03-17','Nequi','Entregado',5880.00,1087654321,'USU002'),
('PED004','2025-03-18','Efectivo','No entregado',4200.00,1076543219,'USU003'),
('PED005','2025-03-19','Daviplata','En camino',9800.00,1065432198,'USU002'),
('PED050','2026-04-09','Efectivo','Entregado',17000.00,1098765432,'USU050'),
('PED051','2026-04-09','Tarjeta','En camino',30000.00,1087654321,'USU051'),
('PED052','2026-04-09','Transferencia','En camino',5200.00,900123456,'USU052');

/*Table structure for table `t_producto` */

DROP TABLE IF EXISTS `t_producto`;

CREATE TABLE `t_producto` (
  `pro_id` varchar(20) NOT NULL COMMENT 'ID del producto',
  `pro_nombre` varchar(100) DEFAULT NULL COMMENT 'Nombre del producto',
  `pro_categoria` varchar(50) DEFAULT NULL COMMENT 'Categoría del producto',
  `pro_descripcion` varchar(255) DEFAULT NULL COMMENT 'Descripción del producto',
  `pro_precio` decimal(12,2) DEFAULT NULL COMMENT 'Precio unitario de venta',
  `pro_cantidad_disponible` int(11) DEFAULT 0 COMMENT 'Stock total disponible (suma de lotes activos)',
  `pro_stock_minimo` int(11) DEFAULT 10 COMMENT 'Stock mínimo para alertas de reposición',
  `pro_fecha_caducidad` date DEFAULT NULL COMMENT 'Fecha de vencimiento del lote activo más próximo',
  `pro_estado` varchar(20) DEFAULT 'Activo' COMMENT 'Estado: Activo / Descontinuado / Suspendido',
  `pro_prov_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del proveedor principal',
  PRIMARY KEY (`pro_id`),
  KEY `pro_prov_id_fk` (`pro_prov_id_fk`),
  CONSTRAINT `producto_ibfk_1` FOREIGN KEY (`pro_prov_id_fk`) REFERENCES `t_proveedor` (`prov_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_producto` */

insert  into `t_producto`(`pro_id`,`pro_nombre`,`pro_categoria`,`pro_descripcion`,`pro_precio`,`pro_cantidad_disponible`,`pro_stock_minimo`,`pro_fecha_caducidad`,`pro_estado`,`pro_prov_id_fk`) values 
('PRO001','Acetaminofen 500','Analgesico','Caja x 10 tab',850.00,200,20,'2026-08-31','Activo','PROV002'),
('PRO002','Ibuprofeno 400','Antiinflamatorio','Caja x 10 tab',1200.00,150,15,'2026-06-30','Activo','PROV001'),
('PRO003','Loratadina 10mg','Antihistaminico','Caja x 10 tab',980.00,80,10,'2027-01-31','Activo','PROV003'),
('PRO004','Suero oral 500ml','Hidratacion','Electrolitos',3500.00,60,10,'2026-12-15','Activo','PROV004'),
('PRO005','Alcohol 70% 250ml','Antiseptico','Uso externo',4200.00,45,8,'2027-05-20','Activo','PROV005'),
('PRO050','Ibuprofeno 400mg','Analgesico','Tabletas x 20 unidades',8500.00,200,20,'2027-06-30','Activo','PROV050'),
('PRO051','Amoxicilina 500mg','Antibiotico','Capsulas x 30 unidades',15000.00,150,15,'2027-09-15','Activo','PROV051'),
('PRO052','Loratadina 10mg','Antialergico','Tabletas x 10 unidades',5200.00,300,25,'2028-01-20','Activo','PROV052'),
('PRO099','Producto Test','Analgesico','Test desc',500.00,50,5,'2027-12-31','Activo','PROV099'),
('PROV099','Proveedor Test',NULL,NULL,NULL,NULL,10,NULL,'Activo',NULL);

/*Table structure for table `t_proveedor` */

DROP TABLE IF EXISTS `t_proveedor`;

CREATE TABLE `t_proveedor` (
  `prov_id` varchar(20) NOT NULL COMMENT 'ID del proveedor',
  `prov_nit` varchar(20) DEFAULT NULL COMMENT 'NIT del proveedor',
  `prov_nombre` varchar(100) DEFAULT NULL COMMENT 'Nombre del proveedor',
  `prov_tipo` varchar(30) DEFAULT 'Laboratorio' COMMENT 'Tipo: Laboratorio / Distribuidor / Importador',
  `prov_contacto` varchar(20) DEFAULT NULL COMMENT 'Teléfono del proveedor',
  `prov_direccion` varchar(100) DEFAULT NULL COMMENT 'Dirección del proveedor',
  `prov_email` varchar(100) DEFAULT NULL COMMENT 'Email del proveedor',
  PRIMARY KEY (`prov_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_proveedor` */

insert  into `t_proveedor`(`prov_id`,`prov_nit`,`prov_nombre`,`prov_tipo`,`prov_contacto`,`prov_direccion`,`prov_email`) values 
('PROV001','800123456-1','Bayer Colombia','Laboratorio','6012345678','Bogota Zona Industrial','ventas@bayer.co'),
('PROV002','900234567-2','Tecnoquimicas','Laboratorio','6027654321','Cali Yumbo','pedidos@tq.com'),
('PROV003','800345678-3','Genfar S.A.','Laboratorio','6038765432','Bogota Autopista Sur','dist@genfar.co'),
('PROV004','900456789-4','Lab. La Sante','Laboratorio','6019876543','Bogota Chia','info@lasante.co'),
('PROV005','800567890-5','Cofarma Ltda','Distribuidor','6054321987','Medellin El Poblado','pedidos@cofarma.com'),
('PROV050','800111222-3','Laboratorios MedPlus','Laboratorio','6017001234','Zona Industrial Bogota','ventas@medplus.com'),
('PROV051','800333444-5','Distribuidora FarmaExpress','Distribuidor','6048005678','Calle 50 #30-20 Medellin','contacto@farmaexpress.co'),
('PROV052','800555666-7','Importadora Global Pharma','Importador','6023009876','Puerto de Buenaventura','info@globalpharma.com'),
('PROV099','999888777-1','Proveedor Test','Distribuidor','6019999999','Bogota Test','test@prov.com');

/*Table structure for table `t_proveedor_producto` */

DROP TABLE IF EXISTS `t_proveedor_producto`;

CREATE TABLE `t_proveedor_producto` (
  `ppp_prov_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del proveedor',
  `ppp_pro_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del producto',
  KEY `ppp_prov_id_fk` (`ppp_prov_id_fk`),
  KEY `ppp_pro_id_fk` (`ppp_pro_id_fk`),
  CONSTRAINT `prov_pro_ibfk_1` FOREIGN KEY (`ppp_prov_id_fk`) REFERENCES `t_proveedor` (`prov_id`),
  CONSTRAINT `prov_pro_ibfk_2` FOREIGN KEY (`ppp_pro_id_fk`) REFERENCES `t_producto` (`pro_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_proveedor_producto` */

insert  into `t_proveedor_producto`(`ppp_prov_id_fk`,`ppp_pro_id_fk`) values 
('PROV002','PRO001'),
('PROV001','PRO002'),
('PROV003','PRO003'),
('PROV004','PRO004'),
('PROV005','PRO005'),
('PROV001','PRO001'),
('PROV050','PRO050'),
('PROV051','PRO051'),
('PROV052','PRO052');

/*Table structure for table `t_reporte` */

DROP TABLE IF EXISTS `t_reporte`;

CREATE TABLE `t_reporte` (
  `rep_id` varchar(20) NOT NULL COMMENT 'ID del reporte',
  `rep_tipo` varchar(50) DEFAULT NULL COMMENT 'Tipo: Ventas / Inventario / Más vendidos / Por vencer',
  `rep_fecha` datetime DEFAULT NULL COMMENT 'Fecha y hora de generación',
  `rep_parametros` varchar(255) DEFAULT NULL COMMENT 'Parámetros usados (fechas, filtros, etc.)',
  `rep_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del usuario que generó el reporte',
  `rep_resultado` text DEFAULT NULL COMMENT 'Resumen del resultado o ruta del archivo exportado',
  PRIMARY KEY (`rep_id`),
  KEY `rep_usu_id_fk` (`rep_usu_id_fk`),
  CONSTRAINT `reporte_ibfk_1` FOREIGN KEY (`rep_usu_id_fk`) REFERENCES `t_usuario` (`usu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_reporte` */

insert  into `t_reporte`(`rep_id`,`rep_tipo`,`rep_fecha`,`rep_parametros`,`rep_usu_id_fk`,`rep_resultado`) values 
('REP001','Ventas','2025-03-19 18:00:00','Desde:2025-03-15 Hasta:2025-03-19','USU005','Total ventas: $41030.00 - 5 pedidos'),
('REP002','Por vencer','2025-03-19 18:05:00','Dias_max:180','USU005','1 producto próximo a vencer: Ibuprofeno 400 (LOT002)'),
('REP050','Ventas','2026-04-09 10:00:00','Mes: Abril 2026','USU051','Total ventas: $52200'),
('REP051','Inventario','2026-04-09 11:00:00','Categoria: Analgesico','USU051','Stock total: 300 unidades'),
('REP052','Por vencer','2026-04-09 14:00:00','Proveedor: PROV050','USU051','Total compras: $850000');

/*Table structure for table `t_rol` */

DROP TABLE IF EXISTS `t_rol`;

CREATE TABLE `t_rol` (
  `rol_id` varchar(20) NOT NULL COMMENT 'ID del rol',
  `rol_nombre` varchar(50) NOT NULL COMMENT 'Nombre del rol (Administrador, Vendedor, Bodeguero)',
  `rol_descripcion` varchar(255) DEFAULT NULL COMMENT 'Descripción del rol y sus permisos',
  `rol_estado` tinyint(1) DEFAULT 1 COMMENT '1=Activo / 0=Inactivo',
  PRIMARY KEY (`rol_id`),
  CONSTRAINT `t_rol_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `t_usuario` (`usu_rol_id_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabla de roles de usuarios';

/*Data for the table `t_rol` */

insert  into `t_rol`(`rol_id`,`rol_nombre`,`rol_descripcion`,`rol_estado`) values 
('ROL001','Administrador','Acceso total al sistema, gestion de usuarios y configuracion',1),
('ROL002','Vendedor','Gestion de ventas, pedidos y facturacion',1),
('ROL003','Bodeguero','Gestion de inventario, compras y lotes',1);

/*Table structure for table `t_sesion` */

DROP TABLE IF EXISTS `t_sesion`;

CREATE TABLE `t_sesion` (
  `ses_id` varchar(60) NOT NULL COMMENT 'Token o ID de sesión (UUID)',
  `ses_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del usuario',
  `ses_fecha_inicio` datetime DEFAULT NULL COMMENT 'Fecha y hora de inicio de sesión',
  `ses_fecha_fin` datetime DEFAULT NULL COMMENT 'Fecha y hora de cierre de sesión',
  `ses_ip` varchar(45) DEFAULT NULL COMMENT 'IP desde donde se inició sesión',
  `ses_activa` tinyint(1) DEFAULT 1 COMMENT '1=Sesión activa / 0=Cerrada',
  PRIMARY KEY (`ses_id`),
  KEY `ses_usu_id_fk` (`ses_usu_id_fk`),
  CONSTRAINT `sesion_ibfk_1` FOREIGN KEY (`ses_usu_id_fk`) REFERENCES `t_usuario` (`usu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_sesion` */

insert  into `t_sesion`(`ses_id`,`ses_usu_id_fk`,`ses_fecha_inicio`,`ses_fecha_fin`,`ses_ip`,`ses_activa`) values 
('SES-001','USU002','2025-03-19 08:05:00','2025-03-19 17:00:00','192.168.1.10',0),
('SES-002','USU003','2025-03-19 08:10:00',NULL,'192.168.1.11',1),
('SES-050','USU050','2026-04-09 08:00:00',NULL,'192.168.1.50',1),
('SES-051','USU051','2026-04-09 09:30:00',NULL,'192.168.1.51',1),
('SES-052','USU052','2026-04-09 07:45:00',NULL,'10.0.0.52',0);

/*Table structure for table `t_usuario` */

DROP TABLE IF EXISTS `t_usuario`;

CREATE TABLE `t_usuario` (
  `usu_id` varchar(20) NOT NULL COMMENT 'ID del usuario',
  `usu_nombre` varchar(100) DEFAULT NULL COMMENT 'Nombre del usuario',
  `usu_rol_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del rol del usuario (FK a t_rol)',
  `usu_correo` varchar(100) DEFAULT NULL COMMENT 'Correo electrónico del usuario',
  `usu_contrasena` varchar(255) DEFAULT NULL COMMENT 'Hash de contraseña (bcrypt recomendado)',
  `usu_estado` tinyint(1) DEFAULT 1 COMMENT 'Estado: 1=Activo / 0=Inactivo',
  `usu_ultimo_acceso` datetime DEFAULT NULL COMMENT 'Fecha y hora del último login',
  PRIMARY KEY (`usu_id`),
  UNIQUE KEY `usu_correo_unique` (`usu_correo`),
  KEY `usu_rol_id_fk` (`usu_rol_id_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_usuario` */

insert  into `t_usuario`(`usu_id`,`usu_nombre`,`usu_rol_id_fk`,`usu_correo`,`usu_contrasena`,`usu_estado`,`usu_ultimo_acceso`) values 
('USU001','Diana Lopez','ROL001','d.lopez@sd.com','$2b$12$59BjXtraY8WfjhvQGCiJzuaT1HTJkS8SH8mtaLzL3xTxUj/Lb2ZgK',1,NULL),
('USU002','Pedro Vargas','ROL002','p.vargas@sd.com','$2b$12$TX8izXrpNEFbDR1dE5qVBeJ5v51dXXhccldogD0dT6tuMFVoAh39W',1,'2025-03-19 08:05:00'),
('USU003','Sandra Nino','ROL002','s.nino@sd.com','$2b$12$Gm5hGB1ELP41oc0NohHM9OtrcNpdZP75Mxxaxb96HFdSgsGUPEYW2',1,'2025-03-19 08:10:00'),
('USU004','Camilo Ruiz','ROL003','c.ruiz@sd.com','$2b$12$C/3B2eDPwo0L49tYymBp/.jDU.qNA3fIAy1R.cCE8mz0J2d/6bjsi',1,'2025-03-12 07:55:00'),
('USU005','Luisa Mora','ROL004','l.mora@sd.com','$2b$12$VaCU2NL494ycZp.BG1X70e3bkZc.Wosoi2e.XiXJzF/.e.2zlQJkq',1,NULL),
('USU050','Andres Gomez','ROL002','andres.gomez@farmacia.com','$2b$12$HKI94lfawJsY1EENyeKBBu2cJgQAwnD6OyU8JrF9PDtBFhVZWUBZ6',1,NULL),
('USU051','Maria Torres','ROL001','maria.torres@farmacia.com','$2b$12$QPLMu0R/x.p2wIrCQv2E1.BGPfGwLAHV2pEa7mti.iy9RskmQJ20i',1,NULL),
('USU052','Pedro Ruiz','ROL003','pedro.ruiz@farmacia.com','$2b$12$mABNj6826p/AP1ubQlFZm.n2F6n0msL2gzVdRthlIxAPTIP/GtQaa',1,NULL),
('USU099','Test User','ROL002','test@sd.com','$2b$12$D1AyTMydROT/YU9H5QHfwOZIyI1VOtn3mQSGGPZhTxeL/04aCN2li',1,NULL);

/*Table structure for table `t_usuario_factura` */

DROP TABLE IF EXISTS `t_usuario_factura`;

CREATE TABLE `t_usuario_factura` (
  `usa_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID del usuario',
  `usa_fac_id_fk` varchar(20) DEFAULT NULL COMMENT 'ID de la factura',
  KEY `usa_usu_id_fk` (`usa_usu_id_fk`),
  KEY `usa_fac_id_fk` (`usa_fac_id_fk`),
  CONSTRAINT `usu_fac_ibfk_1` FOREIGN KEY (`usa_usu_id_fk`) REFERENCES `t_usuario` (`usu_id`),
  CONSTRAINT `usu_fac_ibfk_2` FOREIGN KEY (`usa_fac_id_fk`) REFERENCES `t_factura` (`fac_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `t_usuario_factura` */

insert  into `t_usuario_factura`(`usa_usu_id_fk`,`usa_fac_id_fk`) values 
('USU002','PED001'),
('USU003','PED002'),
('USU002','PED003'),
('USU003','PED004'),
('USU002','PED005');

/*Table structure for table `t_token_revocado` */

DROP TABLE IF EXISTS `t_token_revocado`;

CREATE TABLE `t_token_revocado` (
  `tre_id` int(11) NOT NULL AUTO_INCREMENT,
  `tre_token_hash` varchar(64) NOT NULL COMMENT 'SHA-256 del token JWT',
  `tre_fecha_revocacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha y hora de revocación',
  `tre_usu_id_fk` varchar(20) DEFAULT NULL COMMENT 'Usuario que cerró sesión',
  PRIMARY KEY (`tre_id`),
  KEY `tre_token_hash` (`tre_token_hash`),
  KEY `tre_usu_id_fk` (`tre_usu_id_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/* Trigger structure for table `t_inventario_movimiento` */

DELIMITER $$

/*!50003 DROP TRIGGER*//*!50032 IF EXISTS */ /*!50003 `trg_monitoria_after_movimiento` */$$

/*!50003 CREATE */ /*!50017 DEFINER = 'root'@'localhost' */ /*!50003 TRIGGER `trg_monitoria_after_movimiento` AFTER INSERT ON `t_inventario_movimiento` FOR EACH ROW 
BEGIN
    DECLARE v_saldo_anterior INT;
    DECLARE v_saldo_actual INT;
    DECLARE v_costo DECIMAL(12,2);
    DECLARE v_nuevo_id VARCHAR(20);

    -- Generar ID basado en timestamp
    SET v_nuevo_id = CONCAT('MON', DATE_FORMAT(NOW(), '%y%m%d%H%i%s'), FLOOR(RAND() * 99));

    -- Obtener stock actual del producto
    SELECT pro_cantidad_disponible, pro_precio 
    INTO v_saldo_anterior, v_costo
    FROM t_producto WHERE pro_id = NEW.inm_pro_id_fk;

    -- Calcular nuevo saldo
    IF NEW.inm_tipo_movimiento = 'Entrada' THEN
        SET v_saldo_actual = v_saldo_anterior + NEW.inm_cantidad;
    ELSEIF NEW.inm_tipo_movimiento = 'Salida' THEN
        SET v_saldo_actual = v_saldo_anterior - NEW.inm_cantidad;
    ELSE
        SET v_saldo_actual = v_saldo_anterior + NEW.inm_cantidad;
    END IF;

    -- Insertar en monitoria
    INSERT INTO t_monitoria (mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, 
                          mon_fecha, mon_tipo, mon_cantidad, mon_saldo_anterior, 
                          mon_saldo_actual, mon_costo_unitario, mon_costo_total)
    VALUES (
        v_nuevo_id,
        NEW.inm_pro_id_fk,
        NEW.inm_lot_id_fk,
        NEW.inm_id,
        NEW.inm_fecha,
        NEW.inm_tipo_movimiento,
        NEW.inm_cantidad,
        v_saldo_anterior,
        v_saldo_actual,
        v_costo,
        NEW.inm_cantidad * v_costo
    );

    -- Actualizar stock del producto
    UPDATE t_producto 
    SET pro_cantidad_disponible = v_saldo_actual 
    WHERE pro_id = NEW.inm_pro_id_fk;

END */$$


DELIMITER ;

/*Table structure for table `v_historial_ventas` */

DROP TABLE IF EXISTS `v_historial_ventas`;

/*!50001 DROP VIEW IF EXISTS `v_historial_ventas` */;
/*!50001 DROP TABLE IF EXISTS `v_historial_ventas` */;

/*!50001 CREATE TABLE  `v_historial_ventas`(
 `cli_id` varchar(20) ,
 `cliente` varchar(101) ,
 `ped_id` varchar(20) ,
 `ped_fecha` date ,
 `ped_metodo_pago` varchar(50) ,
 `ped_estado_entrega` varchar(50) ,
 `ped_total` decimal(12,2) ,
 `producto` varchar(100) ,
 `det_cantidad` int(11) ,
 `det_precio_unitario` decimal(12,2) ,
 `det_subtotal` decimal(12,2) 
)*/;

/*Table structure for table `v_mas_vendidos` */

DROP TABLE IF EXISTS `v_mas_vendidos`;

/*!50001 DROP VIEW IF EXISTS `v_mas_vendidos` */;
/*!50001 DROP TABLE IF EXISTS `v_mas_vendidos` */;

/*!50001 CREATE TABLE  `v_mas_vendidos`(
 `pro_id` varchar(20) ,
 `pro_nombre` varchar(100) ,
 `pro_categoria` varchar(50) ,
 `total_unidades_vendidas` decimal(32,0) ,
 `total_ingresos` decimal(34,2) 
)*/;

/*Table structure for table `v_proximos_vencer` */

DROP TABLE IF EXISTS `v_proximos_vencer`;

/*!50001 DROP VIEW IF EXISTS `v_proximos_vencer` */;
/*!50001 DROP TABLE IF EXISTS `v_proximos_vencer` */;

/*!50001 CREATE TABLE  `v_proximos_vencer`(
 `pro_id` varchar(20) ,
 `pro_nombre` varchar(100) ,
 `lot_numero` varchar(50) ,
 `lot_fecha_vencimiento` date ,
 `dias_restantes` int(7) ,
 `lot_cantidad_actual` int(11) 
)*/;

/*Table structure for table `v_stock_minimo` */

DROP TABLE IF EXISTS `v_stock_minimo`;

/*!50001 DROP VIEW IF EXISTS `v_stock_minimo` */;
/*!50001 DROP TABLE IF EXISTS `v_stock_minimo` */;

/*!50001 CREATE TABLE  `v_stock_minimo`(
 `pro_id` varchar(20) ,
 `pro_nombre` varchar(100) ,
 `pro_categoria` varchar(50) ,
 `stock_actual` int(11) ,
 `stock_minimo` int(11) 
)*/;

/*View structure for view v_historial_ventas */

/*!50001 DROP TABLE IF EXISTS `v_historial_ventas` */;
/*!50001 DROP VIEW IF EXISTS `v_historial_ventas` */;

/*!50001 CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_historial_ventas` AS select `c`.`cli_id` AS `cli_id`,concat(`c`.`cli_nombre`,' ',`c`.`cli_apellido`) AS `cliente`,`p`.`ped_id` AS `ped_id`,`p`.`ped_fecha` AS `ped_fecha`,`p`.`ped_metodo_pago` AS `ped_metodo_pago`,`p`.`ped_estado_entrega` AS `ped_estado_entrega`,`p`.`ped_total` AS `ped_total`,`pr`.`pro_nombre` AS `producto`,`d`.`det_cantidad` AS `det_cantidad`,`d`.`det_precio_unitario` AS `det_precio_unitario`,`d`.`det_subtotal` AS `det_subtotal` from (((`t_pedido` `p` join `t_cliente` `c` on(`p`.`ped_cli_id_fk` = `c`.`cli_id`)) join `t_detalle_pedido` `d` on(`d`.`det_ped_id_fk` = `p`.`ped_id`)) join `t_producto` `pr` on(`d`.`det_pro_id_fk` = `pr`.`pro_id`)) */;

/*View structure for view v_mas_vendidos */

/*!50001 DROP TABLE IF EXISTS `v_mas_vendidos` */;
/*!50001 DROP VIEW IF EXISTS `v_mas_vendidos` */;

/*!50001 CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_mas_vendidos` AS select `pr`.`pro_id` AS `pro_id`,`pr`.`pro_nombre` AS `pro_nombre`,`pr`.`pro_categoria` AS `pro_categoria`,sum(`d`.`det_cantidad`) AS `total_unidades_vendidas`,sum(`d`.`det_subtotal`) AS `total_ingresos` from ((`t_detalle_pedido` `d` join `t_producto` `pr` on(`d`.`det_pro_id_fk` = `pr`.`pro_id`)) join `t_pedido` `p` on(`d`.`det_ped_id_fk` = `p`.`ped_id`)) where `p`.`ped_estado_entrega` <> 'Anulado' group by `pr`.`pro_id`,`pr`.`pro_nombre`,`pr`.`pro_categoria` order by sum(`d`.`det_cantidad`) desc */;

/*View structure for view v_proximos_vencer */

/*!50001 DROP TABLE IF EXISTS `v_proximos_vencer` */;
/*!50001 DROP VIEW IF EXISTS `v_proximos_vencer` */;

/*!50001 CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_proximos_vencer` AS select `p`.`pro_id` AS `pro_id`,`p`.`pro_nombre` AS `pro_nombre`,`l`.`lot_numero` AS `lot_numero`,`l`.`lot_fecha_vencimiento` AS `lot_fecha_vencimiento`,to_days(`l`.`lot_fecha_vencimiento`) - to_days(curdate()) AS `dias_restantes`,`l`.`lot_cantidad_actual` AS `lot_cantidad_actual` from (`t_lote` `l` join `t_producto` `p` on(`l`.`lot_pro_id_fk` = `p`.`pro_id`)) where `l`.`lot_estado` = 'Activo' and to_days(`l`.`lot_fecha_vencimiento`) - to_days(curdate()) between 0 and 180 order by to_days(`l`.`lot_fecha_vencimiento`) - to_days(curdate()) */;

/*View structure for view v_stock_minimo */

/*!50001 DROP TABLE IF EXISTS `v_stock_minimo` */;
/*!50001 DROP VIEW IF EXISTS `v_stock_minimo` */;

/*!50001 CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_stock_minimo` AS select `t_producto`.`pro_id` AS `pro_id`,`t_producto`.`pro_nombre` AS `pro_nombre`,`t_producto`.`pro_categoria` AS `pro_categoria`,`t_producto`.`pro_cantidad_disponible` AS `stock_actual`,`t_producto`.`pro_stock_minimo` AS `stock_minimo` from `t_producto` where `t_producto`.`pro_cantidad_disponible` <= `t_producto`.`pro_stock_minimo` and `t_producto`.`pro_estado` = 'Activo' */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

/* Nuevas columnas y tablas agregadas durante el desarrollo */

-- Columnas para comprobante de pago en pedidos
ALTER TABLE t_pedido ADD COLUMN IF NOT EXISTS ped_comprobante LONGBLOB DEFAULT NULL AFTER ped_cuenta_bancaria;
ALTER TABLE t_pedido ADD COLUMN IF NOT EXISTS ped_comprobante_tipo VARCHAR(50) DEFAULT NULL AFTER ped_comprobante;

-- Columnas para comprobante de pago en compras
ALTER TABLE t_compra ADD COLUMN IF NOT EXISTS com_comprobante LONGBLOB DEFAULT NULL AFTER com_observacion;
ALTER TABLE t_compra ADD COLUMN IF NOT EXISTS com_comprobante_tipo VARCHAR(50) DEFAULT NULL AFTER com_comprobante;

-- Columna para trazabilidad por lote en detalle de pedido
ALTER TABLE t_detalle_pedido ADD COLUMN IF NOT EXISTS det_lot_id_fk VARCHAR(20) DEFAULT NULL AFTER det_pro_id_fk;

-- Columnas para control sanitario (INVIMA y control especial) en productos
ALTER TABLE t_producto ADD COLUMN IF NOT EXISTS pro_registro_invima VARCHAR(50) DEFAULT NULL AFTER pro_fecha_caducidad;
ALTER TABLE t_producto ADD COLUMN IF NOT EXISTS pro_fecha_vencimiento_registro DATE DEFAULT NULL AFTER pro_registro_invima;
ALTER TABLE t_producto ADD COLUMN IF NOT EXISTS pro_control_especial TINYINT(1) DEFAULT 0 AFTER pro_fecha_vencimiento_registro;
ALTER TABLE t_producto ADD COLUMN IF NOT EXISTS pro_tipo_control VARCHAR(50) DEFAULT NULL AFTER pro_control_especial;

-- Columna para cuenta bancaria en facturas
ALTER TABLE t_factura ADD COLUMN IF NOT EXISTS fac_cuenta_bancaria VARCHAR(100) DEFAULT NULL AFTER fac_forma_pago;

-- Tabla de devoluciones
CREATE TABLE IF NOT EXISTS t_devolucion (
  dev_id VARCHAR(20) NOT NULL PRIMARY KEY,
  dev_ped_id_fk VARCHAR(20) DEFAULT NULL,
  dev_pro_id_fk VARCHAR(20) DEFAULT NULL,
  dev_lot_id_fk VARCHAR(20) DEFAULT NULL,
  dev_cantidad INT DEFAULT NULL,
  dev_motivo TEXT DEFAULT NULL,
  dev_fecha DATE DEFAULT NULL,
  dev_usu_id_fk VARCHAR(20) DEFAULT NULL,
  KEY dev_ped_id_fk (dev_ped_id_fk),
  KEY dev_pro_id_fk (dev_pro_id_fk),
  KEY dev_lot_id_fk (dev_lot_id_fk),
  KEY dev_usu_id_fk (dev_usu_id_fk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Columna para estado de pago en pedidos
ALTER TABLE t_pedido ADD COLUMN IF NOT EXISTS ped_estado_pago VARCHAR(20) DEFAULT 'Pendiente' COMMENT 'Estado del pago: Pendiente / Verificado / Rechazado' AFTER ped_estado_entrega;