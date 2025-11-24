from flask import Blueprint, render_template
from app.dao.referenciales.empleado.empleado_dao import EmpleadoDao
from app.dao.gestionar_compras.registrar_presupuesto_proveedor.presupuesto_de_proveedor_dao import PresupuestoProvDao

ocmod = Blueprint('ocmod', __name__, template_folder='templates')

@ocmod.route('/ordenes-index')
def ordenes_index():
    return render_template('orden-index.html')

@ocmod.route('/ordenes-gestion')
def ordenes_gestion():
    empdao = EmpleadoDao()
    presupuestodao = PresupuestoProvDao()

    # Obtener solo presupuestos aprobados
    todos_presupuestos = presupuestodao.obtener_presupuestos()
    presupuestos_aprobados = [p for p in todos_presupuestos if p['estado'] == 'Aprobado']

    return render_template(
        'orden-gestion.html',
        empleados=empdao.get_empleados(),
        presupuestos=presupuestos_aprobados
    )