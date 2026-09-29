-- =============================================================================
-- PROYECTO: SISTEMA INTEGRAL DE GESTIÓN - BARBERÍA HERNÁNDEZ
-- MOTOR: PostgreSQL 14+
-- ARCHIVO: sql/esquemas.sql
-- TOTAL DE TABLAS REGISTRADAS: 21
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. LIMPIEZA PREVENTIVA
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS facturacion_pagos CASCADE;
DROP TABLE IF EXISTS facturacion_detalles CASCADE;
DROP TABLE IF EXISTS facturacion CASCADE;
DROP TABLE IF EXISTS factura_pagos CASCADE;
DROP TABLE IF EXISTS factura_detalles CASCADE;
DROP TABLE IF EXISTS facturas CASCADE;
DROP TABLE IF EXISTS cita_detalles CASCADE;
DROP TABLE IF EXISTS citas CASCADE;
DROP TABLE IF EXISTS asistencias_barbero CASCADE;
DROP TABLE IF EXISTS horarios_barbero CASCADE;
DROP TABLE IF EXISTS gastos_operativos CASCADE;
DROP TABLE IF EXISTS movimientos_inventario CASCADE;
DROP TABLE IF EXISTS productos CASCADE;
DROP TABLE IF EXISTS servicios CASCADE;
DROP TABLE IF EXISTS promociones CASCADE;
DROP TABLE IF EXISTS proveedores CASCADE;
DROP TABLE IF EXISTS metodos_pago CASCADE;
DROP TABLE IF EXISTS barberos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS categorias CASCADE;

-- -----------------------------------------------------------------------------
-- 1. TABLAS BASE Y AUTENTICACIÓN
-- -----------------------------------------------------------------------------

-- 1. categorias
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Servicio', 'Producto')),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    creado_en TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. usuarios (Login web con roles Administrador / Cliente)
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    cedula VARCHAR(15) UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    rol VARCHAR(30) NOT NULL DEFAULT 'Cliente' CHECK (rol IN ('Administrador', 'Cliente', 'Barbero')),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    creado_en TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. clientes (Directorio físico / Fidelidad)
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(15) UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(150),
    fecha_nacimiento DATE,
    puntos_fidelidad INTEGER NOT NULL DEFAULT 0 CHECK (puntos_fidelidad >= 0),
    preferencias TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    fecha_registro TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. barberos
CREATE TABLE barberos (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    dni_cedula VARCHAR(20) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(150),
    direccion VARCHAR(255),
    fecha_contratacion DATE DEFAULT CURRENT_DATE,
    porcentaje_comision NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (porcentaje_comision BETWEEN 0.00 AND 100.00),
    sueldo_base NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (sueldo_base >= 0.00),
    foto_url VARCHAR(255),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    creado_en TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. metodos_pago
CREATE TABLE metodos_pago (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL UNIQUE,
    comision_porcentaje NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (comision_porcentaje >= 0.00),
    requiere_referencia BOOLEAN NOT NULL DEFAULT FALSE,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

-- 6. proveedores
CREATE TABLE proveedores (
    ruc VARCHAR(20) PRIMARY KEY,
    empresa VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    direccion VARCHAR(255),
    ciudad VARCHAR(100),
    nombre_contacto VARCHAR(150),
    telefono_contacto VARCHAR(20),
    dias_credito INTEGER NOT NULL DEFAULT 0 CHECK (dias_credito >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    creado_en TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. promociones
CREATE TABLE promociones (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo_cupon VARCHAR(20) UNIQUE,
    porcentaje_desc NUMERIC(5,2) CHECK (porcentaje_desc BETWEEN 0.00 AND 100.00),
    monto_fijo_desc NUMERIC(10,2) CHECK (monto_fijo_desc >= 0.00),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    CONSTRAINT chk_rango_fechas_promo CHECK (fecha_fin >= fecha_inicio)
);

-- -----------------------------------------------------------------------------
-- 2. OPERACIÓN, INVENTARIO Y SERVICIOS
-- -----------------------------------------------------------------------------

-- 8. servicios
CREATE TABLE servicios (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    duracion_minutos INTEGER NOT NULL CHECK (duracion_minutos > 0),
    precio NUMERIC(10,2) NOT NULL CHECK (precio >= 0.00),
    costo_interno NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (costo_interno >= 0.00),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    creado_en TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    codigo_barras VARCHAR(50) UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    precio NUMERIC(10,2) NOT NULL CHECK (precio >= 0.00),
    costo NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (costo >= 0.00),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    stock_minimo INTEGER NOT NULL DEFAULT 5 CHECK (stock_minimo >= 0),
    unidad_medida VARCHAR(20) DEFAULT 'Unidad',
    uso_interno BOOLEAN NOT NULL DEFAULT FALSE,
    imagen_url TEXT,
    proveedor_ruc VARCHAR(20) REFERENCES proveedores(ruc) ON UPDATE CASCADE ON DELETE SET NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo')),
    creado_en TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. horarios_barbero
CREATE TABLE horarios_barbero (
    id SERIAL PRIMARY KEY,
    barbero_id INTEGER NOT NULL REFERENCES barberos(id) ON DELETE CASCADE,
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
    hora_entrada TIME NOT NULL,
    hora_salida TIME NOT NULL,
    inicio_descanso TIME,
    fin_descanso TIME,
    CONSTRAINT chk_horas_coherentes CHECK (hora_salida > hora_entrada)
);

-- 11. asistencias_barbero
CREATE TABLE asistencias_barbero (
    id SERIAL PRIMARY KEY,
    barbero_id INTEGER NOT NULL REFERENCES barberos(id) ON DELETE CASCADE,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    hora_llegada TIME,
    hora_salida TIME,
    estado VARCHAR(20) NOT NULL DEFAULT 'Presente' CHECK (estado IN ('Presente', 'Falta', 'Permiso', 'Atraso'))
);

-- 12. gastos_operativos
CREATE TABLE gastos_operativos (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(50) NOT NULL,
    monto NUMERIC(10,2) NOT NULL CHECK (monto > 0.00),
    fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE,
    descripcion TEXT,
    metodo_pago VARCHAR(50) DEFAULT 'Efectivo'
);

-- 13. movimientos_inventario
CREATE TABLE movimientos_inventario (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    tipo_movimiento VARCHAR(20) NOT NULL CHECK (tipo_movimiento IN ('IN', 'OUT', 'LOSS', 'INTERNAL')),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    fecha_hora TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    motivo VARCHAR(150)
);

-- -----------------------------------------------------------------------------
-- 3. MÓDULO DE CITAS
-- -----------------------------------------------------------------------------

-- 14. citas
CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id) ON UPDATE CASCADE ON DELETE SET NULL,
    usuario_id INTEGER REFERENCES usuarios(id) ON UPDATE CASCADE ON DELETE SET NULL,
    barbero_id INTEGER NOT NULL REFERENCES barberos(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    duracion_estimada_min INTEGER NOT NULL DEFAULT 30 CHECK (duracion_estimada_min > 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente' 
        CHECK (estado IN ('Pendiente', 'Confirmada', 'Atendida', 'Cancelada', 'No Asistio')),
    notas_cliente TEXT,
    motivo_cancelacion VARCHAR(255),
    creado_en TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 15. cita_detalles
CREATE TABLE cita_detalles (
    id SERIAL PRIMARY KEY,
    cita_id INTEGER NOT NULL REFERENCES citas(id) ON DELETE CASCADE,
    servicio_id INTEGER NOT NULL REFERENCES servicios(id) ON DELETE RESTRICT,
    precio_congelado NUMERIC(10,2) NOT NULL CHECK (precio_congelado >= 0.00)
);

-- -----------------------------------------------------------------------------
-- 4. FACTURACIÓN ACTIVA (LA QUE UTILIZA TU SISTEMA WEB ACTUALMENTE)
-- -----------------------------------------------------------------------------

-- 16. facturacion
CREATE TABLE facturacion (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(50) NOT NULL UNIQUE,
    fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tipo_operacion VARCHAR(20) NOT NULL DEFAULT 'Venta' CHECK (tipo_operacion IN ('Venta', 'Compra')),
    usuario_id INTEGER REFERENCES usuarios(id) ON UPDATE CASCADE ON DELETE SET NULL,
    cliente_id INTEGER REFERENCES usuarios(id) ON UPDATE CASCADE ON DELETE SET NULL,
    proveedor_ruc VARCHAR(20) REFERENCES proveedores(ruc) ON UPDATE CASCADE ON DELETE SET NULL,
    cita_id INTEGER UNIQUE REFERENCES citas(id) ON UPDATE CASCADE ON DELETE SET NULL,
    promocion_id INTEGER REFERENCES promociones(id) ON UPDATE CASCADE ON DELETE SET NULL,
    subtotal NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (subtotal >= 0.00),
    descuento NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (descuento >= 0.00),
    iva NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (iva >= 0.00),
    total NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (total >= 0.00),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo', 'Pagada', 'Anulada')),
    impresiones_contador INTEGER NOT NULL DEFAULT 0 CHECK (impresiones_contador >= 0)
);

-- 17. facturacion_detalles
CREATE TABLE facturacion_detalles (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturacion(id) ON DELETE CASCADE,
    tipo_item VARCHAR(20) NOT NULL DEFAULT 'Producto' CHECK (tipo_item IN ('Producto', 'Servicio')),
    barbero_id INTEGER REFERENCES barberos(id) ON UPDATE CASCADE ON DELETE SET NULL,
    servicio_id INTEGER REFERENCES servicios(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    producto_id INTEGER REFERENCES productos(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    descripcion VARCHAR(255) NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario >= 0.00),
    subtotal NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0.00)
);

-- 18. facturacion_pagos
CREATE TABLE facturacion_pagos (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturacion(id) ON DELETE CASCADE,
    metodo_pago VARCHAR(50) NOT NULL DEFAULT 'Efectivo',
    monto NUMERIC(10,2) NOT NULL CHECK (monto > 0.00),
    referencia VARCHAR(100),
    fecha_pago TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(30) NOT NULL DEFAULT 'Aprobado'
);

-- -----------------------------------------------------------------------------
-- 5. TABLAS DE COMPATIBILIDAD HISTÓRICA / RESPALDO
-- -----------------------------------------------------------------------------

-- 19. facturas
CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    num_factura VARCHAR(50) NOT NULL UNIQUE,
    cliente_id INTEGER REFERENCES clientes(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    cita_id INTEGER UNIQUE REFERENCES citas(id) ON UPDATE CASCADE ON DELETE SET NULL,
    promocion_id INTEGER REFERENCES promociones(id) ON UPDATE CASCADE ON DELETE SET NULL,
    fecha_emision TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    subtotal NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    descuento NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    impuestos NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    total NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pagada',
    impresiones_contador INTEGER NOT NULL DEFAULT 0
);

-- 20. factura_detalles
CREATE TABLE factura_detalles (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas(id) ON DELETE CASCADE,
    barbero_id INTEGER REFERENCES barberos(id) ON UPDATE CASCADE ON DELETE SET NULL,
    servicio_id INTEGER REFERENCES servicios(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    producto_id INTEGER REFERENCES productos(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario NUMERIC(10,2) NOT NULL,
    subtotal_linea NUMERIC(10,2) NOT NULL
);

-- 21. factura_pagos
CREATE TABLE factura_pagos (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas(id) ON DELETE CASCADE,
    metodo_pago_id INTEGER REFERENCES metodos_pago(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    monto_pagado NUMERIC(10,2) NOT NULL,
    referencia_transaccion VARCHAR(100),
    fecha_pago TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 6. DATOS SEMILLA (INSERTS)
-- -----------------------------------------------------------------------------
INSERT INTO categorias (nombre, tipo, estado) VALUES
('Cuidado Capilar', 'Producto', 'Activo'),
('Cuidado de Barba', 'Producto', 'Activo'),
('Herramientas y Accesorios', 'Producto', 'Activo'),
('Cortes Clásicos y Modernos', 'Servicio', 'Activo'),
('Afeitado y Perfilado Tradicional', 'Servicio', 'Activo'),
('Tratamientos Faciales Masculinos', 'Servicio', 'Activo')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO metodos_pago (descripcion, comision_porcentaje, requiere_referencia, estado) VALUES
('Efectivo', 0.00, FALSE, 'Activo'),
('Transferencia Bancaria', 0.00, TRUE, 'Activo'),
('Tarjeta de Débito/Crédito', 0.00, TRUE, 'Activo'),
('Deuna / QR', 0.00, TRUE, 'Activo')
ON CONFLICT (descripcion) DO NOTHING;