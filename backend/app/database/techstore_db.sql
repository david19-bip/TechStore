-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 23-11-2026 a las 19:26:08
-- Versión del servidor: 10.11.16-MariaDB
-- Versión de PHP: 8.5.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `techstore_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auditoria`
--

CREATE TABLE `auditoria` (
  `id_auditoria` bigint(20) UNSIGNED NOT NULL,
  `id_usuario` int(10) UNSIGNED DEFAULT NULL,
  `tabla_afectada` varchar(64) NOT NULL,
  `registro_id` varchar(64) NOT NULL,
  `accion` enum('INSERT','UPDATE','DELETE','LOGIN','LOGOUT') NOT NULL,
  `datos_anteriores` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`datos_anteriores`)),
  `datos_nuevos` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`datos_nuevos`)),
  `direccion_ip` varchar(45) DEFAULT NULL,
  `fecha_evento` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `auditoria`
--

INSERT INTO `auditoria` (`id_auditoria`, `id_usuario`, `tabla_afectada`, `registro_id`, `accion`, `datos_anteriores`, `datos_nuevos`, `direccion_ip`, `fecha_evento`) VALUES
(1, 1, 'compras', '1', 'INSERT', NULL, '{\"numero_factura\": \"FC-2026-0001\", \"total\": 1487500.00}', '127.0.0.1', '2026-11-23 18:25:36');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id_categoria` int(10) UNSIGNED NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `estado` enum('activa','inactiva') NOT NULL DEFAULT 'activa',
  `creado_en` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `estado`, `creado_en`) VALUES
(1, 'Periféricos', 'Teclados, mouse, diademas y accesorios', 'activa', '2026-11-23 18:25:36'),
(2, 'Portátiles', 'Computadores portátiles para oficina y gaming', 'activa', '2026-11-23 18:25:36'),
(3, 'Almacenamiento', 'Discos SSD, NVMe y memorias USB', 'activa', '2026-11-23 18:25:36');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id_cliente` int(10) UNSIGNED NOT NULL,
  `tipo_documento` enum('CC','CE','NIT','PASAPORTE') NOT NULL DEFAULT 'CC',
  `numero_documento` varchar(30) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `telefono` varchar(25) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `ciudad` varchar(80) DEFAULT NULL,
  `estado` enum('activo','inactivo') NOT NULL DEFAULT 'activo',
  `creado_en` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`id_cliente`, `tipo_documento`, `numero_documento`, `nombre`, `apellido`, `telefono`, `email`, `direccion`, `ciudad`, `estado`, `creado_en`) VALUES
(1, 'CC', '1012345678', 'Andrés', 'Martínez', '3209876543', 'andres.martinez@correo.com', 'Calle 20 # 5-12', 'Soacha', 'activo', '2026-11-23 18:25:36');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `compras`
--

CREATE TABLE `compras` (
  `id_compra` int(10) UNSIGNED NOT NULL,
  `id_proveedor` int(10) UNSIGNED NOT NULL,
  `id_usuario` int(10) UNSIGNED NOT NULL,
  `numero_factura` varchar(50) NOT NULL,
  `fecha_compra` datetime NOT NULL DEFAULT current_timestamp(),
  `subtotal` decimal(14,2) NOT NULL DEFAULT 0.00,
  `impuesto` decimal(14,2) NOT NULL DEFAULT 0.00,
  `total` decimal(14,2) NOT NULL DEFAULT 0.00,
  `estado` enum('pendiente','recibida','anulada') NOT NULL DEFAULT 'pendiente',
  `observaciones` varchar(255) DEFAULT NULL
) ;

--
-- Volcado de datos para la tabla `compras`
--

INSERT INTO `compras` (`id_compra`, `id_proveedor`, `id_usuario`, `numero_factura`, `fecha_compra`, `subtotal`, `impuesto`, `total`, `estado`, `observaciones`) VALUES
(1, 1, 1, 'FC-2026-0001', '2026-11-23 13:25:36', 1250000.00, 237500.00, 1487500.00, 'recibida', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_compras`
--

CREATE TABLE `detalle_compras` (
  `id_detalle_compra` int(10) UNSIGNED NOT NULL,
  `id_compra` int(10) UNSIGNED NOT NULL,
  `id_producto` int(10) UNSIGNED NOT NULL,
  `cantidad` int(10) UNSIGNED NOT NULL,
  `precio_unitario` decimal(12,2) NOT NULL,
  `subtotal` decimal(14,2) GENERATED ALWAYS AS (`cantidad` * `precio_unitario`) STORED
) ;

--
-- Volcado de datos para la tabla `detalle_compras`
--

INSERT INTO `detalle_compras` (`id_detalle_compra`, `id_compra`, `id_producto`, `cantidad`, `precio_unitario`) VALUES
(1, 1, 1, 10, 55000.00),
(2, 1, 2, 5, 140000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_ventas`
--

CREATE TABLE `detalle_ventas` (
  `id_detalle_venta` int(10) UNSIGNED NOT NULL,
  `id_venta` int(10) UNSIGNED NOT NULL,
  `id_producto` int(10) UNSIGNED NOT NULL,
  `cantidad` int(10) UNSIGNED NOT NULL,
  `precio_unitario` decimal(12,2) NOT NULL,
  `descuento` decimal(12,2) NOT NULL DEFAULT 0.00,
  `subtotal` decimal(14,2) GENERATED ALWAYS AS (`cantidad` * `precio_unitario` - `descuento`) STORED
) ;

--
-- Volcado de datos para la tabla `detalle_ventas`
--

INSERT INTO `detalle_ventas` (`id_detalle_venta`, `id_venta`, `id_producto`, `cantidad`, `precio_unitario`, `descuento`) VALUES
(1, 1, 1, 1, 85000.00, 0.00),
(2, 1, 2, 1, 210000.00, 0.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `movimientos_inventario`
--

CREATE TABLE `movimientos_inventario` (
  `id_movimiento` int(10) UNSIGNED NOT NULL,
  `id_producto` int(10) UNSIGNED NOT NULL,
  `id_usuario` int(10) UNSIGNED NOT NULL,
  `id_compra` int(10) UNSIGNED DEFAULT NULL,
  `id_venta` int(10) UNSIGNED DEFAULT NULL,
  `tipo_movimiento` enum('entrada_compra','salida_venta','ajuste_positivo','ajuste_negativo','devolucion') NOT NULL,
  `cantidad` int(10) UNSIGNED NOT NULL,
  `stock_anterior` int(11) NOT NULL,
  `stock_nuevo` int(11) NOT NULL,
  `motivo` varchar(255) DEFAULT NULL,
  `fecha_movimiento` datetime NOT NULL DEFAULT current_timestamp()
) ;

--
-- Volcado de datos para la tabla `movimientos_inventario`
--

INSERT INTO `movimientos_inventario` (`id_movimiento`, `id_producto`, `id_usuario`, `id_compra`, `id_venta`, `tipo_movimiento`, `cantidad`, `stock_anterior`, `stock_nuevo`, `motivo`, `fecha_movimiento`) VALUES
(1, 1, 1, 1, NULL, 'entrada_compra', 10, 6, 16, 'Ingreso por factura FC-2026-0001', '2026-11-23 13:25:36'),
(2, 1, 2, NULL, 1, 'salida_venta', 1, 16, 15, 'Salida por factura FV-2026-0001', '2026-11-23 13:25:36');

--
-- Disparadores `movimientos_inventario`
--
DELIMITER $$
CREATE TRIGGER `trg_movinv_validar_origen_ins` BEFORE INSERT ON `movimientos_inventario` FOR EACH ROW BEGIN
    IF NEW.id_compra IS NOT NULL AND NEW.id_venta IS NOT NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un movimiento de inventario no puede asociarse simultáneamente a una compra y a una venta.';
    END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `trg_movinv_validar_origen_upd` BEFORE UPDATE ON `movimientos_inventario` FOR EACH ROW BEGIN
    IF NEW.id_compra IS NOT NULL AND NEW.id_venta IS NOT NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un movimiento de inventario no puede asociarse simultáneamente a una compra y a una venta.';
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(10) UNSIGNED NOT NULL,
  `id_categoria` int(10) UNSIGNED NOT NULL,
  `sku` varchar(50) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `marca` varchar(80) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `precio_compra` decimal(12,2) NOT NULL,
  `precio_venta` decimal(12,2) NOT NULL,
  `stock_actual` int(11) NOT NULL DEFAULT 0,
  `stock_minimo` int(11) NOT NULL DEFAULT 5,
  `estado` enum('activo','inactivo') NOT NULL DEFAULT 'activo',
  `creado_en` timestamp NOT NULL DEFAULT current_timestamp(),
  `actualizado_en` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `id_categoria`, `sku`, `nombre`, `marca`, `descripcion`, `precio_compra`, `precio_venta`, `stock_actual`, `stock_minimo`, `estado`, `creado_en`, `actualizado_en`) VALUES
(1, 1, 'PER-MOU-001', 'Mouse Gamer RGB 6400 DPI', 'Logitech', 'Mouse óptico ergonómico con 6 botones programables', 55000.00, 85000.00, 15, 5, 'activo', '2026-11-23 18:25:36', '2026-11-23 18:25:36'),
(2, 1, 'PER-TEC-002', 'Teclado Mecánico Switch Red', 'Redragon', 'Teclado mecánico compacto retroiluminado RGB', 140000.00, 210000.00, 10, 3, 'activo', '2026-11-23 18:25:36', '2026-11-23 18:25:36'),
(3, 3, 'ALM-SSD-003', 'SSD NVMe M.2 1TB', 'Kingston', 'Unidad de estado sólido PCIe 4.0', 220000.00, 310000.00, 8, 4, 'activo', '2026-11-23 18:25:36', '2026-11-23 18:25:36');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedores`
--

CREATE TABLE `proveedores` (
  `id_proveedor` int(10) UNSIGNED NOT NULL,
  `nit` varchar(30) NOT NULL,
  `razon_social` varchar(150) NOT NULL,
  `nombre_contacto` varchar(120) DEFAULT NULL,
  `telefono` varchar(25) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `ciudad` varchar(80) DEFAULT NULL,
  `estado` enum('activo','inactivo') NOT NULL DEFAULT 'activo',
  `creado_en` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `proveedores`
--

INSERT INTO `proveedores` (`id_proveedor`, `nit`, `razon_social`, `nombre_contacto`, `telefono`, `email`, `direccion`, `ciudad`, `estado`, `creado_en`) VALUES
(1, '900123456-7', 'Distribuidora Tech Colombia S.A.S.', 'Carlos Pérez', '3105551234', 'ventas@distritech.co', 'Cra 15 # 78-40', 'Bogotá', 'activo', '2026-11-23 18:25:36');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(10) UNSIGNED NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `rol` enum('administrador','vendedor','bodeguero') NOT NULL DEFAULT 'vendedor',
  `estado` enum('activo','inactivo') NOT NULL DEFAULT 'activo',
  `creado_en` timestamp NOT NULL DEFAULT current_timestamp(),
  `actualizado_en` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `email`, `password_hash`, `rol`, `estado`, `creado_en`, `actualizado_en`) VALUES
(1, 'David', 'Ramírez', 'admin@techstore.com', '$2y$10$EjemploHashSeguroAdmin1234567890', 'administrador', 'activo', '2026-11-23 18:25:36', '2026-11-23 18:25:36'),
(2, 'Laura', 'Gómez', 'vendedor@techstore.com', '$2y$10$EjemploHashSeguroVend1234567890', 'vendedor', 'activo', '2026-11-23 18:25:36', '2026-11-23 18:25:36');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `id_venta` int(10) UNSIGNED NOT NULL,
  `id_cliente` int(10) UNSIGNED NOT NULL,
  `id_usuario` int(10) UNSIGNED NOT NULL,
  `numero_factura` varchar(50) NOT NULL,
  `fecha_venta` datetime NOT NULL DEFAULT current_timestamp(),
  `metodo_pago` enum('efectivo','tarjeta','transferencia','pse') NOT NULL DEFAULT 'efectivo',
  `subtotal` decimal(14,2) NOT NULL DEFAULT 0.00,
  `impuesto` decimal(14,2) NOT NULL DEFAULT 0.00,
  `descuento_total` decimal(14,2) NOT NULL DEFAULT 0.00,
  `total` decimal(14,2) NOT NULL DEFAULT 0.00,
  `estado` enum('pendiente','pagada','anulada') NOT NULL DEFAULT 'pagada',
  `observaciones` varchar(255) DEFAULT NULL
) ;

--
-- Volcado de datos para la tabla `ventas`
--

INSERT INTO `ventas` (`id_venta`, `id_cliente`, `id_usuario`, `numero_factura`, `fecha_venta`, `metodo_pago`, `subtotal`, `impuesto`, `descuento_total`, `total`, `estado`, `observaciones`) VALUES
(1, 1, 2, 'FV-2026-0001', '2026-11-23 13:25:36', 'transferencia', 295000.00, 56050.00, 0.00, 351050.00, 'pagada', NULL);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `auditoria`
--
ALTER TABLE `auditoria`
  ADD PRIMARY KEY (`id_auditoria`),
  ADD KEY `idx_auditoria_usuario_fecha` (`id_usuario`,`fecha_evento`),
  ADD KEY `idx_auditoria_tabla_registro` (`tabla_afectada`,`registro_id`),
  ADD KEY `idx_auditoria_accion_fecha` (`accion`,`fecha_evento`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id_categoria`),
  ADD UNIQUE KEY `uq_categorias_nombre` (`nombre`),
  ADD KEY `idx_categorias_estado` (`estado`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`id_cliente`),
  ADD UNIQUE KEY `uq_clientes_documento` (`tipo_documento`,`numero_documento`),
  ADD UNIQUE KEY `uq_clientes_email` (`email`),
  ADD KEY `idx_clientes_nombre_apellido` (`apellido`,`nombre`),
  ADD KEY `idx_clientes_estado` (`estado`);

--
-- Indices de la tabla `compras`
--
ALTER TABLE `compras`
  ADD PRIMARY KEY (`id_compra`),
  ADD UNIQUE KEY `uq_compras_proveedor_factura` (`id_proveedor`,`numero_factura`),
  ADD KEY `idx_compras_proveedor` (`id_proveedor`),
  ADD KEY `idx_compras_usuario` (`id_usuario`),
  ADD KEY `idx_compras_fecha_estado` (`fecha_compra`,`estado`);

--
-- Indices de la tabla `detalle_compras`
--
ALTER TABLE `detalle_compras`
  ADD PRIMARY KEY (`id_detalle_compra`),
  ADD UNIQUE KEY `uq_detalle_compras_compra_prod` (`id_compra`,`id_producto`),
  ADD KEY `idx_detalle_compras_compra` (`id_compra`),
  ADD KEY `idx_detalle_compras_producto` (`id_producto`);

--
-- Indices de la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  ADD PRIMARY KEY (`id_detalle_venta`),
  ADD UNIQUE KEY `uq_detalle_ventas_venta_prod` (`id_venta`,`id_producto`),
  ADD KEY `idx_detalle_ventas_venta` (`id_venta`),
  ADD KEY `idx_detalle_ventas_producto` (`id_producto`);

--
-- Indices de la tabla `movimientos_inventario`
--
ALTER TABLE `movimientos_inventario`
  ADD PRIMARY KEY (`id_movimiento`),
  ADD KEY `idx_movinv_producto_fecha` (`id_producto`,`fecha_movimiento`),
  ADD KEY `idx_movinv_usuario` (`id_usuario`),
  ADD KEY `idx_movinv_tipo_fecha` (`tipo_movimiento`,`fecha_movimiento`),
  ADD KEY `idx_movinv_compra` (`id_compra`),
  ADD KEY `idx_movinv_venta` (`id_venta`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`),
  ADD UNIQUE KEY `uq_productos_sku` (`sku`),
  ADD KEY `idx_productos_categoria` (`id_categoria`),
  ADD KEY `idx_productos_nombre` (`nombre`),
  ADD KEY `idx_productos_marca_estado` (`marca`,`estado`);

--
-- Indices de la tabla `proveedores`
--
ALTER TABLE `proveedores`
  ADD PRIMARY KEY (`id_proveedor`),
  ADD UNIQUE KEY `uq_proveedores_nit` (`nit`),
  ADD UNIQUE KEY `uq_proveedores_email` (`email`),
  ADD KEY `idx_proveedores_razon_social` (`razon_social`),
  ADD KEY `idx_proveedores_ciudad_estado` (`ciudad`,`estado`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `uq_usuarios_email` (`email`),
  ADD KEY `idx_usuarios_rol_estado` (`rol`,`estado`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`id_venta`),
  ADD UNIQUE KEY `uq_ventas_numero_factura` (`numero_factura`),
  ADD KEY `idx_ventas_cliente` (`id_cliente`),
  ADD KEY `idx_ventas_usuario` (`id_usuario`),
  ADD KEY `idx_ventas_fecha_estado` (`fecha_venta`,`estado`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `auditoria`
--
ALTER TABLE `auditoria`
  MODIFY `id_auditoria` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id_categoria` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `id_cliente` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `compras`
--
ALTER TABLE `compras`
  MODIFY `id_compra` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle_compras`
--
ALTER TABLE `detalle_compras`
  MODIFY `id_detalle_compra` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  MODIFY `id_detalle_venta` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `movimientos_inventario`
--
ALTER TABLE `movimientos_inventario`
  MODIFY `id_movimiento` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `proveedores`
--
ALTER TABLE `proveedores`
  MODIFY `id_proveedor` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `id_venta` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `auditoria`
--
ALTER TABLE `auditoria`
  ADD CONSTRAINT `fk_auditoria_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `compras`
--
ALTER TABLE `compras`
  ADD CONSTRAINT `fk_compras_proveedor` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_compras_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `detalle_compras`
--
ALTER TABLE `detalle_compras`
  ADD CONSTRAINT `fk_detalle_compras_compra` FOREIGN KEY (`id_compra`) REFERENCES `compras` (`id_compra`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_detalle_compras_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  ADD CONSTRAINT `fk_detalle_ventas_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_detalle_ventas_venta` FOREIGN KEY (`id_venta`) REFERENCES `ventas` (`id_venta`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `movimientos_inventario`
--
ALTER TABLE `movimientos_inventario`
  ADD CONSTRAINT `fk_movinv_compra` FOREIGN KEY (`id_compra`) REFERENCES `compras` (`id_compra`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_movinv_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_movinv_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_movinv_venta` FOREIGN KEY (`id_venta`) REFERENCES `ventas` (`id_venta`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `fk_productos_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `fk_ventas_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_ventas_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
