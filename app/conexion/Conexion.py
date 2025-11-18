import psycopg2

class Conexion:

    """Metodo constructor
    """

    def __init__(self):
        self.con = psycopg2.connect("dbname=sistemagbd host=localhost user=postgres password=4803")

        """getConexión

            retorna la instancia de la base de datos

        """
    def getConexion(self):
        return self.con