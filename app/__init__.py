from flask import Flask 
## instancia para arrancar el proyecto
app = Flask (__name__)


# importar referenciales
from app.rutas.referenciales.ciudad.ciudad_routes import ciumod

# registrar referenciales 
modulo0 = '/referenciales'
app.register_blueprint(ciumod, url_prefix=f'{modulo0}/ciudad')