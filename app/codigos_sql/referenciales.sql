CREATE TABLE ciudades (
    ciudad_id SERIAL PRIMARY KEY, -- Clave primaria autoincremental
    descripcion VARCHAR(60) unique -- Columna de descripción
);

SELECT id, descripcion 
FROM ciudades;

CREATE TABLE paises (
    id_pais SERIAL PRIMARY KEY,	-- Clave primaria autoincremental
    descripcion VARCHAR(60) UNIQUE-- Columna de descripción
);

CREATE TABLE nacionalidades (
    id SERIAL PRIMARY KEY,	-- Clave primaria autoincremental
    descripcion VARCHAR(60) UNIQUE-- Columna de descripción
);

CREATE TABLE cargos (
    id_cargo SERIAL PRIMARY KEY, 
    descripcion VARCHAR(60) unique 
);

CREATE TABLE estado_civil (
    id_ec SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) NOT NULL
);

CREATE TABLE sexo (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) NOT NULL
);

CREATE TABLE marcas (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) NOT NULL
);

CREATE TABLE emisoras (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) NOT NULL
);

CREATE TABLE tipo_producto (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) NOT NULL
);

CREATE TABLE proveedores(
    id_proveedor PRIMARY KEY
    , ruc VARCHAR(20) UNIQUE NOT NULL
    , razon_social VARCHAR(70) NOT NULL
    , direccion VARCHAR(70) NOT NULL
    , telefono VARCHAR(20) NOT NULL   
);

CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY,         
    direccion TEXT NOT NULL,                 
    telefono VARCHAR(20),                   
    FOREIGN KEY (id_cliente) REFERENCES personas(id_persona) ON DELETE RESTRICT ON UPDATE CASCADE
);

