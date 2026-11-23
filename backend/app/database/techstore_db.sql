-- ============================================================================
--  TechStore - Sistema web para la gestion de inventario, compras y ventas
--  Actividad 2: Diseno e implementacion de la base de datos
--  Motor: MySQL 8.0 / MariaDB 10.4 o superior
--  Autores: David (estructura original) + equipo TechStore
-- ----------------------------------------------------------------------------
--  CONTENIDO
--    0. Creacion de la base de datos
--    1. Tablas maestras      : usuarios, categorias, proveedores, clientes
--    2. Tablas de catalogo   : productos
--    3. Tablas transaccionales: compras, detalle_compras, ventas, detalle_ventas
--    4. Tablas de control    : movimientos_inventario, auditoria
--    5. Datos de prueba (ejecucion opcional, bloque marcado al final)
--    6. Consultas de verificacion
-- ----------------------------------------------------------------------------
--  ORDEN DE CREACION: respeta las dependencias de las claves foraneas, de modo
--  que el script puede ejecutarse completo en un servidor vacio.
-- ============================================================================

DROP DATABASE IF EXISTS techstore_db;
CREATE DATABASE techstore_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE techstore_db;

SET NAMES utf8mb4;
SET time_zone = '+00:00';
SET SQL_MODE = 'STRICT_TRANS_TABLES,NO_AUTO_VALUE_ON_ZERO,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';


-- ============================================================================
-- 1. TABLAS MAESTRAS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- usuarios: personal que opera el sistema. El rol determina los permisos
-- (Actividad 6). 'bodeguero' es el perfil ENCARGADO DE INVENTARIO.
-- ----------------------------------------------------------------------------
CREATE TABLE usuarios (
    id_usuario      INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(100)    NOT NULL,
    apellido        VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    rol             ENUM('administrador','vendedor','bodeguero') NOT NULL DEFAULT 'vendedor',
    estado          ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
    creado_en       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario),
    UNIQUE KEY uq_usuarios_email (email),
    KEY idx_usuarios_rol_estado (rol, estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- categorias: clasificacion de los productos (perifericos, portatiles, etc.)
-- ----------------------------------------------------------------------------
CREATE TABLE categorias (
    id_categoria    INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(80)     NOT NULL,
    descripcion     VARCHAR(255)    DEFAULT NULL,
    estado          ENUM('activa','inactiva') NOT NULL DEFAULT 'activa',
    creado_en       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_categoria),
    UNIQUE KEY uq_categorias_nombre (nombre),
    KEY idx_categorias_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- proveedores: empresas que abastecen la tienda
-- ----------------------------------------------------------------------------
CREATE TABLE proveedores (
    id_proveedor    INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    nit             VARCHAR(30)     NOT NULL,
    razon_social    VARCHAR(150)    NOT NULL,
    nombre_contacto VARCHAR(120)    DEFAULT NULL,
    telefono        VARCHAR(25)     DEFAULT NULL,
    email           VARCHAR(150)    DEFAULT NULL,
    direccion       VARCHAR(200)    DEFAULT NULL,
    ciudad          VARCHAR(80)     DEFAULT NULL,
    estado          ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
    creado_en       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_proveedor),
    UNIQUE KEY uq_proveedores_nit (nit),
    UNIQUE KEY uq_proveedores_email (email),
    KEY idx_proveedores_razon_social (razon_social),
    KEY idx_proveedores_ciudad_estado (ciudad, estado),
    CONSTRAINT chk_proveedores_email CHECK (email IS NULL OR email LIKE '%_@_%.__%')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- clientes: compradores registrados. La identificacion es unica por tipo de
-- documento (una CC y un NIT pueden coincidir en el numero, pero no dos CC
-- con el mismo numero).
-- ----------------------------------------------------------------------------
CREATE TABLE clientes (
    id_cliente      INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    tipo_documento  ENUM('CC','CE','NIT','PASAPORTE') NOT NULL DEFAULT 'CC',
    numero_documento VARCHAR(30)    NOT NULL,
    nombre          VARCHAR(100)    NOT NULL,
    apellido        VARCHAR(100)    NOT NULL,
    telefono        VARCHAR(25)     DEFAULT NULL,
    email           VARCHAR(150)    DEFAULT NULL,
    direccion       VARCHAR(200)    DEFAULT NULL,
    ciudad          VARCHAR(80)     DEFAULT NULL,
    estado          ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
    creado_en       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_cliente),
    UNIQUE KEY uq_clientes_documento (tipo_documento, numero_documento),
    UNIQUE KEY uq_clientes_email (email),
    KEY idx_clientes_nombre_apellido (apellido, nombre),
    KEY idx_clientes_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- 2. TABLA DE CATALOGO
-- ============================================================================

-- ----------------------------------------------------------------------------
-- productos: existencias y precios. stock_actual se modifica solo desde las
-- operaciones de compra, venta o ajuste, y cada cambio deja un registro en
-- movimientos_inventario. Los CHECK impiden precios y cantidades negativas.
-- ----------------------------------------------------------------------------
CREATE TABLE productos (
    id_producto     INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    id_categoria    INT UNSIGNED    NOT NULL,
    sku             VARCHAR(50)     NOT NULL,
    nombre          VARCHAR(150)    NOT NULL,
    marca           VARCHAR(80)     NOT NULL,
    descripcion     TEXT            DEFAULT NULL,
    precio_compra   DECIMAL(12,2)   NOT NULL,
    precio_venta    DECIMAL(12,2)   NOT NULL,
    stock_actual    INT             NOT NULL DEFAULT 0,
    stock_minimo    INT             NOT NULL DEFAULT 5,
    estado          ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
    creado_en       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_producto),
    UNIQUE KEY uq_productos_sku (sku),
    KEY idx_productos_categoria (id_categoria),
    KEY idx_productos_nombre (nombre),
    KEY idx_productos_marca_estado (marca, estado),
    KEY idx_productos_stock (stock_actual, stock_minimo),
    CONSTRAINT fk_productos_categoria FOREIGN KEY (id_categoria)
        REFERENCES categorias (id_categoria) ON UPDATE CASCADE,
    CONSTRAINT chk_productos_precio_compra CHECK (precio_compra >= 0),
    CONSTRAINT chk_productos_precio_venta  CHECK (precio_venta  >= 0),
    CONSTRAINT chk_productos_stock        CHECK (stock_actual >= 0 AND stock_minimo >= 0),
    CONSTRAINT chk_productos_precio_logico CHECK (precio_venta >= precio_compra)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- 3. TABLAS TRANSACCIONALES (compras y ventas con sus tablas de detalle)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- compras: encabezado de la factura del proveedor. subtotal, impuesto y total
-- los calcula el backend dentro de la transaccion; estado 'recibida' es el
-- unico que incrementa existencias.
-- ----------------------------------------------------------------------------
CREATE TABLE compras (
    id_compra       INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    id_proveedor    INT UNSIGNED    NOT NULL,
    id_usuario      INT UNSIGNED    NOT NULL,
    numero_factura  VARCHAR(50)     NOT NULL,
    fecha_compra    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal        DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    impuesto        DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    total           DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    estado          ENUM('pendiente','recibida','anulada') NOT NULL DEFAULT 'pendiente',
    observaciones   VARCHAR(255)    DEFAULT NULL,
    PRIMARY KEY (id_compra),
    UNIQUE KEY uq_compras_proveedor_factura (id_proveedor, numero_factura),
    KEY idx_compras_proveedor (id_proveedor),
    KEY idx_compras_usuario (id_usuario),
    KEY idx_compras_fecha_estado (fecha_compra, estado),
    CONSTRAINT fk_compras_proveedor FOREIGN KEY (id_proveedor)
        REFERENCES proveedores (id_proveedor) ON UPDATE CASCADE,
    CONSTRAINT fk_compras_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario) ON UPDATE CASCADE,
    CONSTRAINT chk_compras_valores CHECK (subtotal >= 0 AND impuesto >= 0 AND total >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- detalle_compras: una fila por producto de la factura. Evita guardar listas
-- de productos en una sola columna (1FN). El subtotal es generado por el motor
-- para que no se pueda desincronizar.
-- ----------------------------------------------------------------------------
CREATE TABLE detalle_compras (
    id_detalle_compra INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_compra       INT UNSIGNED    NOT NULL,
    id_producto     INT UNSIGNED    NOT NULL,
    cantidad        INT UNSIGNED    NOT NULL,
    precio_unitario DECIMAL(12,2)   NOT NULL,
    subtotal        DECIMAL(14,2)   GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    PRIMARY KEY (id_detalle_compra),
    UNIQUE KEY uq_detalle_compras_compra_prod (id_compra, id_producto),
    KEY idx_detalle_compras_compra (id_compra),
    KEY idx_detalle_compras_producto (id_producto),
    CONSTRAINT fk_detalle_compras_compra FOREIGN KEY (id_compra)
        REFERENCES compras (id_compra) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detalle_compras_producto FOREIGN KEY (id_producto)
        REFERENCES productos (id_producto) ON UPDATE CASCADE,
    CONSTRAINT chk_detalle_compras_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_compras_precio CHECK (precio_unitario >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- ventas: encabezado de la factura de venta. descuento_total acumula los
-- descuentos por linea; el total lo confirma el backend en una transaccion.
-- ----------------------------------------------------------------------------
CREATE TABLE ventas (
    id_venta        INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    id_cliente      INT UNSIGNED    NOT NULL,
    id_usuario      INT UNSIGNED    NOT NULL,
    numero_factura  VARCHAR(50)     NOT NULL,
    fecha_venta     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metodo_pago     ENUM('efectivo','tarjeta','transferencia','pse') NOT NULL DEFAULT 'efectivo',
    subtotal        DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    impuesto        DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    descuento_total DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    total           DECIMAL(14,2)   NOT NULL DEFAULT 0.00,
    estado          ENUM('pendiente','pagada','anulada') NOT NULL DEFAULT 'pagada',
    observaciones   VARCHAR(255)    DEFAULT NULL,
    PRIMARY KEY (id_venta),
    UNIQUE KEY uq_ventas_numero_factura (numero_factura),
    KEY idx_ventas_cliente (id_cliente),
    KEY idx_ventas_usuario (id_usuario),
    KEY idx_ventas_fecha_estado (fecha_venta, estado),
    CONSTRAINT fk_ventas_cliente FOREIGN KEY (id_cliente)
        REFERENCES clientes (id_cliente) ON UPDATE CASCADE,
    CONSTRAINT fk_ventas_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario) ON UPDATE CASCADE,
    CONSTRAINT chk_ventas_valores CHECK (subtotal >= 0 AND impuesto >= 0
        AND descuento_total >= 0 AND total >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- detalle_ventas: una fila por producto vendido. El descuento es por linea y
-- el subtotal se calcula como cantidad * precio - descuento.
-- ----------------------------------------------------------------------------
CREATE TABLE detalle_ventas (
    id_detalle_venta INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    id_venta        INT UNSIGNED    NOT NULL,
    id_producto     INT UNSIGNED    NOT NULL,
    cantidad        INT UNSIGNED    NOT NULL,
    precio_unitario DECIMAL(12,2)   NOT NULL,
    descuento       DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    subtotal        DECIMAL(14,2)   GENERATED ALWAYS AS (cantidad * precio_unitario - descuento) STORED,
    PRIMARY KEY (id_detalle_venta),
    UNIQUE KEY uq_detalle_ventas_venta_prod (id_venta, id_producto),
    KEY idx_detalle_ventas_venta (id_venta),
    KEY idx_detalle_ventas_producto (id_producto),
    CONSTRAINT fk_detalle_ventas_venta FOREIGN KEY (id_venta)
        REFERENCES ventas (id_venta) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detalle_ventas_producto FOREIGN KEY (id_producto)
        REFERENCES productos (id_producto) ON UPDATE CASCADE,
    CONSTRAINT chk_detalle_ventas_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_ventas_precio CHECK (precio_unitario >= 0),
    CONSTRAINT chk_detalle_ventas_descuento CHECK (descuento >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- 4. TABLAS DE CONTROL
-- ============================================================================

-- ----------------------------------------------------------------------------
-- movimientos_inventario: historial (kardex) de cada cambio de existencias.
-- Guarda stock anterior y nuevo como evidencia del movimiento. Un movimiento
-- proviene de una compra, de una venta o de un ajuste manual, nunca de dos
-- origenes a la vez (lo validan los triggers).
-- ----------------------------------------------------------------------------
CREATE TABLE movimientos_inventario (
    id_movimiento   INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    id_producto     INT UNSIGNED    NOT NULL,
    id_usuario      INT UNSIGNED    NOT NULL,
    id_compra       INT UNSIGNED    DEFAULT NULL,
    id_venta        INT UNSIGNED    DEFAULT NULL,
    tipo_movimiento ENUM('entrada_compra','salida_venta','ajuste_positivo','ajuste_negativo','devolucion') NOT NULL,
    cantidad        INT UNSIGNED    NOT NULL,
    stock_anterior  INT             NOT NULL,
    stock_nuevo     INT             NOT NULL,
    motivo          VARCHAR(255)    DEFAULT NULL,
    fecha_movimiento DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_movimiento),
    KEY idx_movinv_producto_fecha (id_producto, fecha_movimiento),
    KEY idx_movinv_usuario (id_usuario),
    KEY idx_movinv_tipo_fecha (tipo_movimiento, fecha_movimiento),
    KEY idx_movinv_compra (id_compra),
    KEY idx_movinv_venta (id_venta),
    CONSTRAINT fk_movinv_compra FOREIGN KEY (id_compra)
        REFERENCES compras (id_compra) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_movinv_producto FOREIGN KEY (id_producto)
        REFERENCES productos (id_producto) ON UPDATE CASCADE,
    CONSTRAINT fk_movinv_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario) ON UPDATE CASCADE,
    CONSTRAINT fk_movinv_venta FOREIGN KEY (id_venta)
        REFERENCES ventas (id_venta) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_movinv_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_movinv_stock CHECK (stock_anterior >= 0 AND stock_nuevo >= 0),
    CONSTRAINT chk_movinv_coherencia CHECK (
        (tipo_movimiento IN ('entrada_compra','ajuste_positivo','devolucion') AND stock_nuevo = stock_anterior + cantidad)
        OR (tipo_movimiento IN ('salida_venta','ajuste_negativo') AND stock_nuevo = stock_anterior - cantidad)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- auditoria: registro de operaciones relevantes. Guarda usuario, modulo,
-- accion, tabla y registro afectado, valores antes y despues, IP y fecha-hora,
-- que es lo que exige la Actividad 6. Si se elimina un usuario, el registro
-- historico se conserva con id_usuario NULL.
-- ----------------------------------------------------------------------------
CREATE TABLE auditoria (
    id_auditoria    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_usuario      INT UNSIGNED    DEFAULT NULL,
    modulo          VARCHAR(50)     DEFAULT NULL,
    tabla_afectada  VARCHAR(64)     NOT NULL,
    registro_id     VARCHAR(64)     NOT NULL,
    accion          ENUM('INSERT','UPDATE','DELETE','LOGIN','LOGOUT') NOT NULL,
    datos_anteriores LONGTEXT       DEFAULT NULL,
    datos_nuevos    LONGTEXT        DEFAULT NULL,
    direccion_ip    VARCHAR(45)     DEFAULT NULL,
    fecha_evento    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_auditoria),
    KEY idx_auditoria_usuario_fecha (id_usuario, fecha_evento),
    KEY idx_auditoria_tabla_registro (tabla_afectada, registro_id),
    KEY idx_auditoria_accion_fecha (accion, fecha_evento),
    KEY idx_auditoria_modulo_fecha (modulo, fecha_evento),
    CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_auditoria_datos_anteriores CHECK (datos_anteriores IS NULL OR JSON_VALID(datos_anteriores)),
    CONSTRAINT chk_auditoria_datos_nuevos CHECK (datos_nuevos IS NULL OR JSON_VALID(datos_nuevos))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- Triggers: un movimiento de inventario no puede estar asociado a una compra
-- y a una venta al mismo tiempo.
-- ----------------------------------------------------------------------------
DELIMITER $$
CREATE TRIGGER trg_movinv_validar_origen_ins
BEFORE INSERT ON movimientos_inventario
FOR EACH ROW
BEGIN
    IF NEW.id_compra IS NOT NULL AND NEW.id_venta IS NOT NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un movimiento de inventario no puede asociarse simultaneamente a una compra y a una venta.';
    END IF;
END
$$

CREATE TRIGGER trg_movinv_validar_origen_upd
BEFORE UPDATE ON movimientos_inventario
FOR EACH ROW
BEGIN
    IF NEW.id_compra IS NOT NULL AND NEW.id_venta IS NOT NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un movimiento de inventario no puede asociarse simultaneamente a una compra y a una venta.';
    END IF;
END
$$
DELIMITER ;


-- ============================================================================
-- 5. DATOS DE PRUEBA (bloque independiente, se puede omitir en produccion)
--    Cumple lo pedido en la Actividad 3: 5 categorias, 10 productos,
--    3 proveedores, 5 clientes y 2 usuarios.
-- ============================================================================
START TRANSACTION;

INSERT INTO usuarios (id_usuario, nombre, apellido, email, password_hash, rol) VALUES
(1, 'David',  'Ramirez', 'admin@techstore.com',    '$2b$12$hashDeEjemploAdminCambiarEnProduccion', 'administrador'),
(2, 'Laura',  'Gomez',   'vendedor@techstore.com', '$2b$12$hashDeEjemploVendCambiarEnProduccion',  'vendedor'),
(3, 'Camilo', 'Rojas',   'bodega@techstore.com',   '$2b$12$hashDeEjemploBodeCambiarEnProduccion',  'bodeguero');

INSERT INTO categorias (id_categoria, nombre, descripcion) VALUES
(1, 'Perifericos',    'Teclados, mouse, diademas y accesorios'),
(2, 'Portatiles',     'Computadores portatiles para oficina y gaming'),
(3, 'Almacenamiento', 'Discos SSD, NVMe y memorias USB'),
(4, 'Celulares',      'Telefonos inteligentes y accesorios'),
(5, 'Monitores',      'Pantallas y monitores de escritorio');

INSERT INTO proveedores (id_proveedor, nit, razon_social, nombre_contacto, telefono, email, ciudad) VALUES
(1, '900123456-1', 'Distribuidora Andina S.A.S.', 'Marta Salazar',  '6014567890', 'ventas@distriandina.com', 'Bogota'),
(2, '900987654-2', 'TecnoImport Ltda.',          'Jorge Pineda',   '6043210987', 'compras@tecnoimport.com', 'Medellin'),
(3, '901555333-3', 'GlobalTech Colombia',         'Diana Cardenas', '6027778899', 'contacto@globaltech.com', 'Cali');

INSERT INTO clientes (id_cliente, tipo_documento, numero_documento, nombre, apellido, telefono, email, direccion, ciudad) VALUES
(1, 'CC', '1012345678', 'Andres', 'Martinez', '3209876543', 'andres.martinez@correo.com', 'Calle 20 # 5-12',  'Soacha'),
(2, 'CC', '1023456789', 'Paula',  'Restrepo', '3104567890', 'paula.restrepo@correo.com',  'Carrera 15 # 80-22', 'Bogota'),
(3, 'CC', '1034567890', 'Jhon',   'Ospina',   '3156781234', 'jhon.ospina@correo.com',     'Calle 45 # 12-08', 'Bogota'),
(4, 'NIT', '901222333-4', 'Almacenes', 'El Sol', '6013456789', 'compras@elsol.com',      'Av. 68 # 22-10',   'Bogota'),
(5, 'CC', '1045678901', 'Sara',   'Cifuentes','3187654321', 'sara.cifuentes@correo.com',  'Calle 7 # 3-45',   'Chia');

INSERT INTO productos (id_producto, id_categoria, sku, nombre, marca, descripcion, precio_compra, precio_venta, stock_actual, stock_minimo) VALUES
(1,  2, 'POR-LEN-001', 'Portatil Lenovo IdeaPad 3',        'Lenovo',    'Ryzen 5, 8 GB RAM, 512 GB SSD', 2000000.00, 2500000.00, 0, 3),
(2,  1, 'PER-MOU-002', 'Mouse inalambrico',                'Logitech',  'Mouse optico inalambrico 2.4 GHz', 35000.00, 55000.00, 0, 5),
(3,  1, 'PER-TEC-003', 'Teclado mecanico',                 'Redragon',  'Teclado mecanico switch red RGB', 120000.00, 180000.00, 0, 4),
(4,  5, 'MON-SAM-004', 'Monitor 24 pulgadas',              'Samsung',   'Monitor LED Full HD 75 Hz', 650000.00, 850000.00, 0, 2),
(5,  3, 'ALM-SSD-005', 'SSD NVMe M.2 1 TB',                'Kingston',  'Unidad de estado solido PCIe 4.0', 220000.00, 310000.00, 0, 3),
(6,  1, 'PER-MOU-006', 'Mouse Gamer RGB 6400 DPI',         'Logitech',  'Mouse optico con 6 botones programables', 55000.00, 85000.00, 0, 5),
(7,  1, 'PER-AUD-007', 'Diadema gamer con microfono',      'HyperX',    'Sonido estereo, conector 3.5 mm', 90000.00, 145000.00, 0, 4),
(8,  2, 'POR-HP-008',  'Portatil HP 15',                   'HP',        'Intel Core i5, 16 GB RAM, 512 GB SSD', 2300000.00, 2900000.00, 0, 2),
(9,  4, 'CEL-XIA-009', 'Celular Xiaomi Redmi Note 13',     'Xiaomi',    '128 GB, 8 GB RAM, camara 108 MP', 780000.00, 1050000.00, 0, 3),
(10, 3, 'ALM-USB-010', 'Memoria USB 64 GB',                'SanDisk',   'USB 3.0, 64 GB', 25000.00, 42000.00, 0, 10);

COMMIT;


-- ============================================================================
-- 6. CONSULTAS DE VERIFICACION (evidencias de la Actividad 2)
--    Nota: antes de probar una venta revisar el stock; despues de una compra o
--    venta comprobar el kardex y la auditoria.
-- ============================================================================

-- 6.1 Tamano y contenido de cada tabla
-- SELECT table_name, table_rows FROM information_schema.tables
--  WHERE table_schema = 'techstore_db' ORDER BY table_name;

-- 6.2 Productos que estan en el stock minimo o por debajo (alerta de reposicion)
-- SELECT id_producto, nombre, stock_actual, stock_minimo
--   FROM productos WHERE stock_actual <= stock_minimo AND estado = 'activo';

-- 6.3 Kardex de un producto con su origen (compra o venta)
-- SELECT m.id_movimiento, p.nombre, m.tipo_movimiento, m.cantidad,
--        m.stock_anterior, m.stock_nuevo, c.numero_factura AS compra,
--        v.numero_factura AS venta, m.fecha_movimiento
--   FROM movimientos_inventario m
--   JOIN productos p ON p.id_producto = m.id_producto
--   LEFT JOIN compras c ON c.id_compra = m.id_compra
--   LEFT JOIN ventas  v ON v.id_venta  = m.id_venta
--  ORDER BY m.id_movimiento DESC;

-- 6.4 Ventas por fecha con su vendedor y cliente
-- SELECT DATE(v.fecha_venta) AS dia, COUNT(*) AS facturas, SUM(v.total) AS ingresos
--   FROM ventas v WHERE v.estado = 'pagada' GROUP BY DATE(v.fecha_venta);

-- ============================================================================
-- Fin del script
-- ============================================================================
