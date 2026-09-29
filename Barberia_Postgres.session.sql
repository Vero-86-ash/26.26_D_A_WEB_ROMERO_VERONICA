-- =============================================================================
-- CONSULTAS DE AUDITORÍA Y REGISTRO SEGURO - BARBERÍA HERNÁNDEZ
-- MOTOR: PostgreSQL (barberia_hernandez_db)
-- =============================================================================

-- 1. CONSULTA DE CATÁLOGOS E INVENTARIO
SELECT * FROM categorias ORDER BY id ASC;
SELECT * FROM productos ORDER BY id ASC;
SELECT * FROM servicios ORDER BY id ASC;

-- 2. CONSULTA DE ACTORES DEL SISTEMA
SELECT * FROM usuarios ORDER BY id ASC;
SELECT * FROM clientes ORDER BY id ASC;
SELECT * FROM proveedores ORDER BY ruc ASC;
SELECT * FROM barberos ORDER BY id ASC;

-- 3. INSERCIÓN SEGURA DEL BARBERO PRINCIPAL
-- Evita errores de llave duplicada si ya fue registrado previamente
INSERT INTO barberos (
    nombre_completo, 
    dni_cedula, 
    telefono, 
    email, 
    direccion, 
    fecha_contratacion, 
    porcentaje_comision, 
    sueldo_base, 
    estado
) 
VALUES (
    'Andres Hernández', 
    '1798765432', 
    '0987654321', 
    'andres@mail.com', 
    'Puembo', 
    '2026-09-13', 
    0.00, 
    0.00, 
    'Activo'
)
ON CONFLICT (dni_cedula) DO NOTHING;

-- 4. CONSULTA DE CITAS Y FACTURACIÓN OPERATIVA
SELECT * FROM citas ORDER BY id DESC;
SELECT * FROM facturacion ORDER BY id DESC;
SELECT * FROM facturacion_detalles ORDER BY id ASC;
SELECT * FROM facturacion_pagos ORDER BY id ASC;