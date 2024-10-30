import psycopg2

class Conexion:

    """Metodo constructor
    """

    def __init__(self):
        self.con = psycopg2.connect("dbname=gestionarcomprasbd host=localhost user=postgres password=123")

        """getConexión

            retorna la instancia de la base de datos

        """
    def getConexion(self):
        return self.con