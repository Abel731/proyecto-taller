from typing import List
from datetime import date
from app.dao.gestionar_compras.registrar_presupuesto_proveedor.dto.presupuesto_prov_detalle_dto \
    import PresupuestoProvDetalleDto
from app.dao.referenciales.estado_presupuesto_proveedor.estado_presupuesto_proveedor_dto \
    import EstadoPresupuestoProveedor

class PresupuestoProvDto:
    def __init__(self, id_presupuesto: int, id_proveedor: int, id_pedido_compra: int, 
                 id_empleado: int, id_sucursal: int, estado: EstadoPresupuestoProveedor, 
                 fecha_presupuesto: date, detalle_presupuesto: List[PresupuestoProvDetalleDto]):

        self.__id_presupuesto = id_presupuesto
        self.__id_proveedor = id_proveedor
        self.__id_pedido_compra = id_pedido_compra
        self.__id_empleado = id_empleado
        self.__id_sucursal = id_sucursal
        self.__estado = estado
        self.__fecha_presupuesto = fecha_presupuesto
        self.__detalle_presupuesto = detalle_presupuesto

    @property
    def id_presupuesto(self) -> int:
        return self.__id_presupuesto

    @id_presupuesto.setter
    def id_presupuesto(self, valor: int):
        self.__id_presupuesto = valor

    @property
    def id_proveedor(self) -> int:
        return self.__id_proveedor

    @id_proveedor.setter
    def id_proveedor(self, valor: int):
        if not valor:
            raise ValueError("El atributo id_proveedor no puede estar vacío")
        self.__id_proveedor = valor

    @property
    def id_pedido_compra(self) -> int:
        return self.__id_pedido_compra

    @id_pedido_compra.setter
    def id_pedido_compra(self, valor: int):
        if not valor:
            raise ValueError("El atributo id_pedido_compra no puede estar vacío")
        self.__id_pedido_compra = valor

    @property
    def id_empleado(self) -> int:
        return self.__id_empleado

    @id_empleado.setter
    def id_empleado(self, valor: int):
        if not valor:
            raise ValueError("El atributo id_empleado no puede estar vacío")
        self.__id_empleado = valor

    @property
    def id_sucursal(self) -> int:
        return self.__id_sucursal

    @id_sucursal.setter
    def id_sucursal(self, valor: int):
        if not valor:
            raise ValueError("El atributo id_sucursal no puede estar vacío")
        self.__id_sucursal = valor

    @property
    def estado(self) -> EstadoPresupuestoProveedor:
        return self.__estado

    @estado.setter
    def estado(self, valor: EstadoPresupuestoProveedor):
        if not isinstance(valor, EstadoPresupuestoProveedor):
            raise ValueError("El atributo estado debe ser de tipo 'EstadoPresupuestoProvDto'")
        self.__estado = valor

    @property
    def fecha_presupuesto(self) -> date:
        return self.__fecha_presupuesto

    @fecha_presupuesto.setter
    def fecha_presupuesto(self, valor: date):
        if not isinstance(valor, date):
            raise ValueError("El atributo fecha_presupuesto debe ser de tipo 'date'")
        self.__fecha_presupuesto = valor

    @property
    def detalle_presupuesto(self) -> List[PresupuestoProvDetalleDto]:
        return self.__detalle_presupuesto

    @detalle_presupuesto.setter
    def detalle_presupuesto(self, valor: List[PresupuestoProvDetalleDto]):
        if not isinstance(valor, list):
            raise ValueError("El atributo detalle_presupuesto debe ser una lista de objetos PresupuestoProvDetalleDto")
        for item in valor:
            if not isinstance(item, PresupuestoProvDetalleDto):
                raise ValueError("Todos los elementos de detalle_presupuesto deben ser instancias de PresupuestoProvDetalleDto")
        self.__detalle_presupuesto = valor