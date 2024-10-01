CREATE TABLE ciudades (
    id SERIAL PRIMARY KEY, -- Clave primaria autoincremental
    descripcion VARCHAR(60) unique -- Columna de descripción
);

SELECT id, descripcion 
FROM ciudades;

CREATE TABLE paises (
    id SERIAL PRIMARY KEY,	-- Clave primaria autoincremental
    descripcion VARCHAR(60) UNIQUE-- Columna de descripción
);

CREATE TABLE nacionalidades (
    id SERIAL PRIMARY KEY,	-- Clave primaria autoincremental
    descripcion VARCHAR(60) UNIQUE-- Columna de descripción
);

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,         -- Clave primaria autoincremental
    descripcion VARCHAR(255) UNIQUE, -- Columna de descripción
    cantidad INTEGER NOT NULL,         -- Columna de cantidad
    precio_unitario DECIMAL(10, 2) NOT NULL -- Columna de precio unitario con hasta 10 dígitos y 2 decimales
);

CREATE TABLE personas (
    id_persona SERIAL PRIMARY KEY,  -- Campo id_persona como clave primaria
    nombres VARCHAR(100) NOT NULL,  -- Columna de nombres con hasta 100 caracteres
    apellidos VARCHAR(100) NOT NULL,  -- Columna de apellidos con hasta 100 caracteres
    nro_cedula INTEGER NOT NULL UNIQUE,  -- Columna de número de cédula, debe ser único
    fecha_nacimiento DATE NOT NULL,  -- Columna de fecha de nacimiento en formato DATE que sirve para guardar fechas
    direccion VARCHAR(255) NOT NULL  -- Columna de dirección, admite letras y números, hasta 255 caracteres
);

CREATE TABLE proveedores (
    id_proveedor SERIAL PRIMARY KEY,  -- ID único para cada proveedor
    id_persona INTEGER,  -- Relación con la tabla de personas (puede ser NULL)
    ruc VARCHAR(20) NOT NULL,  -- Registro Único de Contribuyente del proveedor
    razon_social VARCHAR(150) NOT NULL,  -- Nombre comercial del proveedor
    registro DATE NOT NULL,  -- Fecha de registro del proveedor
    estado VARCHAR(20) NOT NULL,  
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona)  -- relación con la tabla de personas
);

CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,         -- ID único para cada cliente
    id_persona INTEGER,                    -- Relación con la tabla de personas
    nombre VARCHAR(100) NOT NULL,          -- Nombre del cliente
    apellido VARCHAR(100) NOT NULL,        -- Apellido del cliente
    cedula VARCHAR(20) NOT null UNIQUE,           -- Cédula del cliente
    direccion VARCHAR(255),                 -- Dirección del cliente
    telefono VARCHAR(20),                   -- Teléfono del cliente
    fecha_registro DATE NOT NULL ,  -- Fecha de registro del cliente R
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona) ON DELETE SET null
);

CREATE TABLE sucursales (
    id_sucursal SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT null UNIQUE,
    direccion VARCHAR(200) NOT NULL,
    telefono integer not null
);

CREATE TABLE depositos (
    id_deposito SERIAL PRIMARY KEY,
    id_sucursal INTEGER,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    telefono INTEGER,
    capacidad INTEGER,
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal) ON DELETE SET null
);