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
    , FOREIGN KEY(id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE estado_de_presupuesto_prov(
    id_estpreprov SERIAL PRIMARY KEY
    , descripcion VARCHAR  NOT NULL
);

ALTER TABLE presupuesto_prov
ADD COLUMN fecha_vencimiento DATE;

ALTER TABLE presupuesto_prov
ALTER COLUMN fecha_vencimiento SET NOT NULL;

SELECT
            pdp.id_presupuesto
            , pdp.id_pedido_compra
            , pdp.id_empleado
            , p.nombres
            , p.apellidos
            , pdp.id_sucursal
            , pdp.id_proveedor
            , prov.ruc
            , prov.razon_social
            , pdp.id_estpreprov
            , edp.descripcion AS estado
            , pdp.fecha_presupuesto
            , pdp.fecha_vencimiento
        FROM
            public.presupuesto_prov pdp
        LEFT JOIN proveedores prov
            ON prov.id_proveedor = pdp.id_proveedor
        LEFT JOIN empleados e
            ON e.id_empleado = pdp.id_empleado
        LEFT JOIN personas p
            ON p.id_persona = e.id_empleado
        LEFT JOIN estado_de_presupuesto_prov edp
            ON edp.id_estpreprov = pdp.id_estpreprov;