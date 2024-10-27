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
    descripcion VARCHAR(60) UNIQUE NOT NULL,
	id_sucursal INTEGER NOT NULL,
	FOREIGN KEY(id_sucursal) REFERENCES
	sucursales(id_sucursal)
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

/*
Presupuesto proveedor
*/

CREATE TABLE presupuesto_prov(
    id_presupuesto SERIAL PRIMARY KEY
    , id_proveedor INTEGER NOT NULL
    , id_pedido_compra INTEGER NOT NULL
    , id_empleado INTEGER NOT NULL
    , id_sucursal INTEGER NOT NULL
    , id_estpreprov INTEGER NOT NULL
    , fecha_presupuesto DATE NOT NULL
    , FOREIGN KEY(id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT ON UPDATE CASCADE
    , FOREIGN KEY(id_pedido_compra) REFERENCES pedido_de_compra(id_pedido_compra) ON DELETE RESTRICT ON UPDATE CASCADE
    , FOREIGN KEY(id_empleado) REFERENCES empleados(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
    , FOREIGN KEY(id_sucursal) REFERENCES sucursales(id_sucursal) ON DELETE RESTRICT ON UPDATE CASCADE
    , FOREIGN KEY(id_estpreprov) REFERENCES estado_de_presupuesto_prov(id_estpreprov) ON DELETE RESTRICT ON UPDATE CASCADE
      
);

CREATE TABLE presupuesto_prov_detalle(
    id_presupuesto INTEGER NOT NULL
    , id_producto INTEGER NOT NULL
    , cantidad INTEGER NOT NULL
    , precio_unitario DECIMAL (10,2)
    , PRIMARY KEY(id_presupuesto, id_producto)
    , FOREIGN KEY(id_presupuesto) REFERENCES presupuesto_prov(id_presupuesto) ON DELETE RESTRICT ON UPDATE CASCADE
    , FOREIGN KEY(id_producto) REFERENCES producto_prov(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE estado_de_presupuesto_prov(
    id_estpreprov SERIAL PRIMARY KEY
    , descripcion VARCHAR UNIQUE NOT NULL
);

CREATE TABLE proveedores(
    id_proveedor INTEGER NOT NULL
    , ruc VARCHAR(20) UNIQUE NOT NULL
    , razon_social VARCHAR(70) NOT NULL
    , direccion VARCHAR(70) NOT NULL
    , telefono VARCHAR(20) NOT NULL   
);

