from flask import Blueprint, render_template
from app.dao.referenciales.sucursal.SurcursalDao import SucursalDao
from app.dao.referenciales.empleado.empleado_dao import EmpleadoDao
from app.dao.referenciales.producto.ProductoDao import ProductoDao
from app.dao.referenciales.proveedor.ProveedorDao import ProveedorDao

pdpmod = Blueprint('pdpmod', __name__, template_folder='templates')

@pdpmod.route('/presupuestos-index')
def presupuestos_index():
    return render_template('presupuestos-index.html')

@pdpmod.route('/presupuestos-agregar')
def presupuestos_agregar():
    sdao = SucursalDao()
    empdao = EmpleadoDao()
    pdao = ProductoDao()
    provdao = ProveedorDao()

    return render_template('presupuestos-agregar.html'\
        , sucursales = sdao.get_sucursales()\
        , empleados = empdao.get_empleados()\
        , productos = pdao.get_productos()
        , proveedores = provdao.get_proveedores())