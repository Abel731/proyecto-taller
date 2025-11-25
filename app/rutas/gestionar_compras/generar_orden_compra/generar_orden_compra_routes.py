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
    presupuestos_aprobados = [p for p in todos_presupuestos if p['estado'] == 'APROBADO']

    return render_template(
        'orden-gestion.html',
        empleados=empdao.get_empleados(),
        presupuestos=presupuestos_aprobados
    )

@ocmod.route('/ordenes-ver/<int:id_orden>')
def ordenes_ver(id_orden):
    """
    Renderiza el formulario para ver/editar una orden existente
    """
    from app.dao.gestionar_compras.generar_orden_compra.orden_compra_dao import OrdenCompraDao
    
    ocdao = OrdenCompraDao()
    
    # Obtener la orden completa
    orden = ocdao.get_orden_por_id(id_orden)
    
    if not orden:
        # Si no existe la orden, redirigir al index con mensaje de error
        from flask import flash, redirect, url_for
        flash(f'No se encontró la orden N° {id_orden}', 'error')
        return redirect(url_for('ocmod.ordenes_index'))
    
    return render_template(
        'orden-ver.html',
        orden=orden
    )