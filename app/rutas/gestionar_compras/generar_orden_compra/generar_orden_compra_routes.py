from flask import Blueprint, render_template, jsonify
from app.dao.referenciales.sucursal.SurcursalDao import SucursalDao
from app.dao.referenciales.empleado.empleado_dao import EmpleadoDao
from app.dao.referenciales.producto.ProductoDao import ProductoDao
from app.dao.referenciales.proveedor.ProveedorDao import ProveedorDao
from app.dao.gestionar_compras.registrar_presupuesto_proveedor.presupuesto_de_proveedor_dao \
    import PresupuestoProvDao

odcmod = Blueprint('odcmod', __name__, template_folder='templates')

@odcmod.route('/ordenes-index')
def ordenes_index():
    return render_template('ordenes-index.html')

@odcmod.route('/ordenes-agregar')
def ordenes_agregar():
    sdao = SucursalDao()
    empdao = EmpleadoDao()
    pdao = ProductoDao()
    provdao = ProveedorDao()
    presupuestodao = PresupuestoProvDao()

    return render_template(
        'ordenes-agregar.html',
        sucursales=sdao.get_sucursales(),
        empleados=empdao.get_empleados(),
        productos=pdao.get_productos(),
        proveedores=provdao.get_proveedores(),
        presupuestos=presupuestodao.obtener_presupuestos_por_fecha()
    )