-- 1. TABLAS CATÁLOGO Y PRINCIPALES (Sin dependencias)

CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('Servicio', 'Producto')),
    estado BOOLEAN DEFAULT TRUE
);

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    fecha_nacimiento DATE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    puntos_fidelidad INTEGER DEFAULT 0,
    preferencias TEXT,
    estado VARCHAR(20) DEFAULT 'Activo'
);

CREATE TABLE barberos (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    dni_cedula VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    direccion VARCHAR(255),
    fecha_contratacion DATE,
    estado VARCHAR(20) DEFAULT 'Activo',
    porcentaje_comision NUMERIC(5,2) DEFAULT 0.00,
    sueldo_base NUMERIC(10,2) DEFAULT 0.00,
    foto_url VARCHAR(255)
);

CREATE TABLE metodos_pago (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL,
    comision_porcentaje NUMERIC(5,2) DEFAULT 0.00,
    requiere_referencia BOOLEAN DEFAULT FALSE
);

CREATE TABLE proveedores (
    ruc VARCHAR(20) PRIMARY KEY,
    empresa VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    direccion VARCHAR(255),
    ciudad VARCHAR(100),
    nombre_contacto VARCHAR(150),
    telefono_contacto VARCHAR(20),
    dias_credito INTEGER DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'Activo'
);

CREATE TABLE promociones (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo_cupon VARCHAR(20) UNIQUE,
    porcentaje_desc NUMERIC(5,2),
    monto_fijo_desc NUMERIC(10,2),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado BOOLEAN DEFAULT TRUE
);

-- 2. TABLAS SECUNDARIAS 

CREATE TABLE servicios (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER REFERENCES categorias(id),
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    duracion_minutos INTEGER NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    costo_interno NUMERIC(10,2) DEFAULT 0.00,
    estado BOOLEAN DEFAULT TRUE
);

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER REFERENCES categorias(id),
    codigo_barras VARCHAR(50) UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    costo_compra NUMERIC(10,2) NOT NULL,
    stock INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 5,
    unidad_medida VARCHAR(20),
    uso_interno BOOLEAN DEFAULT FALSE,
    proveedor_ruc VARCHAR(20) REFERENCES proveedores(ruc)
);

CREATE TABLE horarios_barbero (
    id SERIAL PRIMARY KEY,
    barbero_id INTEGER REFERENCES barberos(id) ON DELETE CASCADE,
    dia_semana INTEGER CHECK (dia_semana BETWEEN 1 AND 7),
    hora_entrada TIME NOT NULL,
    hora_salida TIME NOT NULL,
    inicio_descanso TIME,
    fin_descanso TIME
);

CREATE TABLE asistencias_barbero (
    id SERIAL PRIMARY KEY,
    barbero_id INTEGER REFERENCES barberos(id) ON DELETE CASCADE,
    fecha DATE DEFAULT CURRENT_DATE,
    hora_llegada TIME,
    hora_salida TIME,
    estado VARCHAR(20) DEFAULT 'Presente'
);

CREATE TABLE gastos_operativos (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(50) NOT NULL,
    monto NUMERIC(10,2) NOT NULL,
    fecha_pago DATE NOT NULL,
    descripcion TEXT,
    metodo_pago_id INTEGER REFERENCES metodos_pago(id)
);

-- 3. TABLAS TRANSACCIONALES 

CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    barbero_id INTEGER REFERENCES barberos(id),
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    estado VARCHAR(20) DEFAULT 'Pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notas_cliente TEXT,
    motivo_cancelacion VARCHAR(150)
);

CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    num_factura VARCHAR(20) UNIQUE NOT NULL,
    cliente_id INTEGER REFERENCES clientes(id),
    promocion_id INTEGER REFERENCES promociones(id),
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal NUMERIC(10,2) NOT NULL,
    impuestos NUMERIC(10,2) DEFAULT 0.00,
    descuento NUMERIC(10,2) DEFAULT 0.00,
    total NUMERIC(10,2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Pagada'
);

CREATE TABLE movimientos_inventario (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER REFERENCES productos(id),
    tipo_movimiento VARCHAR(20) CHECK (tipo_movimiento IN ('IN', 'OUT', 'LOSS', 'INTERNAL')),
    cantidad INTEGER NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    motivo VARCHAR(150)
);

-- 4. TABLAS DE DETALLE

CREATE TABLE cita_detalles (
    id SERIAL PRIMARY KEY,
    cita_id INTEGER REFERENCES citas(id) ON DELETE CASCADE,
    servicio_id INTEGER REFERENCES servicios(id),
    precio_congelado NUMERIC(10,2) NOT NULL
);

CREATE TABLE factura_detalles (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id) ON DELETE CASCADE,
    barbero_id INTEGER REFERENCES barberos(id),
    servicio_id INTEGER REFERENCES servicios(id),
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario NUMERIC(10,2) NOT NULL,
    subtotal_linea NUMERIC(10,2) NOT NULL
);

CREATE TABLE factura_pagos (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id) ON DELETE CASCADE,
    metodo_pago_id INTEGER REFERENCES metodos_pago(id),
    monto_pagado NUMERIC(10,2) NOT NULL,
    referencia_transaccion VARCHAR(100)
);