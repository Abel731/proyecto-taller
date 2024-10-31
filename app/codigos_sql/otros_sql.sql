-- SELECT
-- 	e.id_empleado,
-- 	, CONCAT(p.nombres,' ',p.apellidos) empleado
-- 	, p.ci
-- FROM empleados e LEFT JOIN personas p ON e.id_empleado = p.id_persona;


-- SELECT
-- 	sd.id_sucursal
-- 	, s.descripcion nombre_sucursal
-- 	, sd.id_deposito
-- 	, d.descripcion nombre_deposito
-- 	, sd.observaciones
-- 	, sd.estado
-- FROM
-- 	sucursal_depositos sd
-- LEFT JOIN depositos d
-- 	ON sd.id_deposito = d.id_deposito
-- LEFT JOIN sucursales s
-- 	ON sd.id_sucursal = s.id_sucursal
-- WHERE
-- 	sd.id_sucursal = 1

CREATE TABLE estado_de_pedido_compras(
    id_epc SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE sucursales(
    id_sucursal SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE depositos(
    id_deposito SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE sucursal_depositos(
    id_sucursal INTEGER NOT NULL,
    id_deposito INTEGER NOT NULL,
    observaciones VARCHAR(60),
    estado BOOLEAN NOT NULL,
    PRIMARY KEY(id_sucursal, id_deposito),
    FOREIGN KEY(id_sucursal) REFERENCES sucursales(id_sucursal)
    ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY(id_deposito) REFERENCES depositos(id_deposito)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE productos(
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(60) UNIQUE NOT NULL,
    cantidad INTEGER,
    precio_unitario DECIMAL (10,2)
);


CREATE TABLE personas(
    id_persona SERIAL PRIMARY KEY,
    nombres VARCHAR(70) NOT NULL,
    apellidos VARCHAR(70) NOT NULL,
    ci TEXT NOT NULL,
    fechanac DATE,
    creacion_fecha DATE NOT NULL,
    creacion_hora TIME NOT NULL,
    creacion_usuario INTEGER NOT NULL,
    modificacion_fecha DATE,
    modificacion_hora TIME,
    modificacion_usuario INTEGER--,
    /*FOREIGN KEY(creacion_usuario) REFERENCES
    usuarios(id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE
    FOREIGN KEY(modificacion_usuario) REFERENCES
    usuarios(id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE*/
);

CREATE TABLE empleados(
    id_empleado INTEGER PRIMARY KEY,
    fecha_ingreso DATE NOT NULL,
    FOREIGN KEY(id_empleado) REFERENCES personas(id_persona)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE usuarios(
    id_usuario INTEGER PRIMARY KEY,
    nickname TEXT NOT NULL,
    clave TEXT NOT NULL,
    estado BOOLEAN NOT NULL
);

CREATE TABLE pedido_de_compra(
    id_pedido_compra SERIAL PRIMARY KEY
    , id_empleado INTEGER NOT NULL
    , id_sucursal INTEGER NOT NULL
    , id_epc INTEGER NOT NULL
    , fecha_pedido DATE NOT NULL
    , id_deposito INTEGER NOT NULL
    , FOREIGN KEY(id_empleado) REFERENCES empleados(id_empleado)
    , FOREIGN KEY(id_sucursal) REFERENCES sucursales(id_sucursal)
    , FOREIGN KEY(id_epc) REFERENCES estado_de_pedido_compras(id_epc)
    , FOREIGN KEY(id_deposito) REFERENCES depositos(id_deposito)
);

CREATE TABLE pedido_de_compra_detalle(
    id_pedido_compra INTEGER NOT NULL
    , id_producto INTEGER NOT NULL
    , cantidad INTEGER NOT NULL
    , PRIMARY KEY(id_pedido_compra, id_producto)
    , FOREIGN KEY(id_pedido_compra) REFERENCES pedido_de_compra(id_pedido_compra) ON DELETE RESTRICT ON UPDATE CASCADE
    , FOREIGN KEY(id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE paises (
    id_pais SERIAL PRIMARY KEY,	-- Clave primaria autoincremental
    descripcion VARCHAR(60) UNIQUE-- Columna de descripción
);

CREATE TABLE ciudades (
    ciudad_id SERIAL PRIMARY KEY, -- Clave primaria autoincremental
    descripcion VARCHAR(60) unique -- Columna de descripción
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
    id_sexo SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) NOT NULL
);

CREATE TABLE marcas (
    id_marcas SERIAL PRIMARY KEY,
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
    id_proveedor SERIAL PRIMARY KEY
    , ruc VARCHAR(20) UNIQUE NOT NULL
    , razon_social VARCHAR(70) NOT NULL
    , direccion VARCHAR(70) NOT NULL
    , telefono VARCHAR(20) NOT NULL   
);

CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,   
    direccion TEXT NOT NULL,                 
    telefono VARCHAR(20),                   
    FOREIGN KEY (id_cliente) REFERENCES personas(id_persona) ON DELETE RESTRICT ON UPDATE CASCADE
);

SELECT 
    c.id_cliente,
    CONCAT(p.nombres, ' ', p.apellidos) AS cliente,
    p.ci	
FROM 
    clientes c
LEFT JOIN 
    personas p ON c.id_cliente = p.id_persona;
