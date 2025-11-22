class ProductoDto:
    
    def __init__(self, id_producto, nombre, precio_compra):
        self.__id_producto = id_producto
        self.__nombre = nombre
        self.__precio_compra = precio_compra

    # Getters y setters de id_producto
    @property
    def id_producto(self):
        return self.__id_producto

    @id_producto.setter
    def id_producto(self, valor):
        if not valor:
            raise ValueError("El atributo id_producto no puede estar vacío")
        self.__id_producto = valor

    # Getters y setters de nombre
    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor:
            raise ValueError("El atributo nombre no puede estar vacío")
        self.__nombre = valor.upper()

    # Getters y setters de precio_compra
    @property
    def precio_compra(self):
        return self.__precio_compra

    @precio_compra.setter
    def precio_compra(self, valor):
        if valor is None or valor < 0:
            raise ValueError("El atributo precio_compra no puede estar vacío ni ser negativo")
        self.__precio_compra = valor