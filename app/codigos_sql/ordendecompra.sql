CREATE TABLE orden_de_compra (
    id_orden SERIAL PRIMARY KEY,
    id_proveedor INTEGER NOT NULL,
    id_presupuesto INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    id_sucursal INTEGER NOT NULL,
    id_estorden INTEGER NOT NULL,
    fecha_orden DATE NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_presupuesto) REFERENCES presupuesto_prov(id_presupuesto) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_estorden) REFERENCES estado_orden_de_compra(id_estorden) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE orden_de_compra_detalle (
    id_orden INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2),
    iva_5 DECIMAL(10,2) DEFAULT 0.00,
    iva_10 DECIMAL(10,2) DEFAULT 0.00, 
    total DECIMAL(10,2) NOT NULL, 
    PRIMARY KEY (id_orden, id_producto),
    FOREIGN KEY (id_orden) REFERENCES orden_de_compra(id_orden) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE estado_orden_de_compra (
    id_estorden SERIAL PRIMARY KEY,
    descripcion VARCHAR NOT NULL Unique
);