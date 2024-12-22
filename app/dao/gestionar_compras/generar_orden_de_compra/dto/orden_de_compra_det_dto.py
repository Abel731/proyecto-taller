class OrdenDeCompraDetalleDto:
    def __init__(self, id_orden: int, id_producto: int, cantidad: int, precio_unitario: float, total: float = 0.00):
        self.__id_orden = id_orden
        self.__id_producto = id_producto
        self.__cantidad = cantidad
        self.__precio_unitario = precio_unitario
        self.__total = total

    @property
    def id_orden(self) -> int:
        return self.__id_orden

    @id_orden.setter
    def id_orden(self, valor: int):
        if not valor:
            raise ValueError("El atributo id_orden no puede estar vacío")
        self.__id_orden = valor

    @property
    def id_producto(self) -> int:
        return self.__id_producto

    @id_producto.setter
    def id_producto(self, valor: int):
        if not valor:
            raise ValueError("El atributo id_producto no puede estar vacío")
        self.__id_producto = valor

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor: int):
        if valor <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        self.__cantidad = valor

    @property
    def precio_unitario(self) -> float:
        return self.__precio_unitario

    @precio_unitario.setter
    def precio_unitario(self, valor: float):
        if valor < 0:
            raise ValueError("El precio_unitario no puede ser negativo")
        self.__precio_unitario = valor

    @property
    def total(self) -> float:
        return self.__total

    @total.setter
    def total(self, valor: float):
        if valor <= 0:
            raise ValueError("El total debe ser mayor a 0")
        self.__total = valor