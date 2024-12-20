from typing import List
from datetime import date
from app.dao.gestionar_compras.generar_orden_de_compra.dto.orden_de_compra_det_dto \
    import OrdenDeCompraDetalleDto

from app.dao.referenciales.estado_orden_compra.estado_orden_compra_dto import EstadoOrdenDeCompraDto

class OrdenDeCompraDto:
    def __init__(self, id_orden: int, id_proveedor: int, id_presupuesto: int, id_empleado: int,
        id_sucursal: int, estado: EstadoOrdenDeCompraDto, fecha_orden: date,
        detalle_orden: List[OrdenDeCompraDetalleDto]
    ):
        self.__id_orden = id_orden
        self.__id_proveedor = id_proveedor
        self.__id_presupuesto = id_presupuesto
        self.__id_empleado = id_empleado
        self.__id_sucursal = id_sucursal
        self.__estado = estado
        self.__fecha_orden = fecha_orden
        self.__detalle_orden = detalle_orden

    @property
    def id_orden(self) -> int:
        return self.__id_orden

    @id_orden.setter
    def id_orden(self, valor: int):
        self.__id_orden = valor

    @property
    def id_proveedor(self) -> int:
        return self.__id_proveedor

    @id_proveedor.setter
    def id_proveedor(self, valor: int):
        if not valor:
            raise ValueError("El atributo id_proveedor no puede estar vacío")
        self.__id_proveedor = valor

    @property
    def id_presupuesto(self) -> int:
        return self.__id_presupuesto

    @id_presupuesto.setter
    def id_presupuesto(self, valor: int):
        if not valor:
            raise ValueError("El atributo id_presupuesto no puede estar vacío")
        self.__id_presupuesto = valor

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
    def estado(self) -> EstadoOrdenDeCompraDto:
        return self.__estado

    @estado.setter
    def estado(self, valor: EstadoOrdenDeCompraDto):
        if not isinstance(valor, EstadoOrdenDeCompraDto):
            raise ValueError("El atributo estado debe ser de tipo 'EstadoOrdenDeCompraDto'")
        self.__estado = valor

    @property
    def fecha_orden(self) -> date:
        return self.__fecha_orden

    @fecha_orden.setter
    def fecha_orden(self, valor: date):
        if not isinstance(valor, date):
            raise ValueError("El atributo fecha_orden debe ser de tipo 'date'")
        self.__fecha_orden = valor

    @property
    def detalle_orden(self) -> List[OrdenDeCompraDetalleDto]:
        return self.__detalle_orden

    @detalle_orden.setter
    def detalle_orden(self, valor: List[OrdenDeCompraDetalleDto]):
        if not isinstance(valor, list):
            raise ValueError("El atributo detalle_orden debe ser una lista de objetos OrdenDeCompraDetalleDto")
        for item in valor:
            if not isinstance(item, OrdenDeCompraDetalleDto):
                raise ValueError("Todos los elementos de detalle_orden deben ser instancias de OrdenDeCompraDetalleDto")
        self.__detalle_orden = valor