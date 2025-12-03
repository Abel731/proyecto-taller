from flask import Blueprint, render_template, redirect, url_for
from app.dao.gestionar_servicios.generar_orden_servicio.generar_orden_servicio_dao import OrdenServicioDao
from app.conexion.Conexion import Conexion

# Crear Blueprint para las vistas HTML
ordenmod = Blueprint('ordenmod', __name__, template_folder='templates')

# ========================================================================
# RUTAS - ORDEN DE SERVICIO
# ========================================================================

# ========== RUTA 1: INDEX (Listado) ==========
@ordenmod.route('/ordenes-servicio')
def ordenes_servicio_index():
    """
    Muestra el listado de todas las órdenes de servicio
    """
    try:
        print("========== DEBUG ROUTE: Cargando index de órdenes de SERVICIO ==========")
        return render_template('orden-servicio-index.html')  # ← CAMBIO AQUÍ
        
    except Exception as e:
        print(f"❌ ERROR en ordenes_servicio_index: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 2: GESTION (Registrar) ==========
@ordenmod.route('/ordenes-servicio-gestion')
def ordenes_servicio_gestion():
    """
    Muestra el formulario para registrar una nueva orden de servicio
    """
    try:
        print("========== DEBUG ROUTE: Iniciando carga de datos para orden de SERVICIO ==========")
        
        dao = OrdenServicioDao()
        
        # ========== OBTENER EMPLEADOS (con su propia conexión) ==========
        print("DEBUG: Ejecutando query empleados...")
        conexion_empleados = Conexion()
        con_emp = conexion_empleados.getConexion()
        cursor_emp = con_emp.cursor()
        
        query_empleados = """
        SELECT e.id_empleado, CONCAT(p.nombres, ' ', p.apellidos) AS empleado, p.ci
        FROM empleados e
        INNER JOIN personas p ON e.id_empleado = p.id_persona
        ORDER BY p.apellidos, p.nombres
        """
        cursor_emp.execute(query_empleados)
        empleados_data = cursor_emp.fetchall()
        
        empleados = []
        for emp in empleados_data:
            empleados.append({
                'id_empleado': emp[0],
                'empleado': emp[1],
                'ci': emp[2]
            })
        
        print(f"DEBUG: Empleados encontrados: {len(empleados)}")
        
        cursor_emp.close()
        con_emp.close()
        
        # ========== OBTENER PRESUPUESTOS APROBADOS (cada uno con su conexión) ==========
        print("DEBUG: Obteniendo presupuestos aprobados...")
        presupuestos_disponibles = dao.obtener_presupuestos_aprobados()
        
        print(f"DEBUG: Presupuestos disponibles: {len(presupuestos_disponibles)}")
        print("DEBUG: Renderizando template...")
        
        return render_template(
            'orden-servicio-gestion.html',  # ← CAMBIO AQUÍ
            empleados=empleados,
            presupuestos_disponibles=presupuestos_disponibles
        )
        
    except Exception as e:
        print(f"❌ ERROR en ordenes_servicio_gestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 3: VER DETALLE ==========
@ordenmod.route('/ordenes-servicio-ver/<int:id_orden_servicio>')
def ordenes_servicio_ver(id_orden_servicio):
    """
    Muestra el detalle de una orden de servicio específica
    """
    try:
        print(f"========== DEBUG ROUTE: Cargando detalle de orden de SERVICIO {id_orden_servicio} ==========")
        
        dao = OrdenServicioDao()
        orden = dao.obtener_por_id(id_orden_servicio)
        
        if not orden:
            print(f"DEBUG: Orden {id_orden_servicio} no encontrada")
            return redirect(url_for('ordenmod.ordenes_servicio_index'))
        
        print(f"DEBUG: Orden encontrada - Estado: {orden['estado']}")
        print("DEBUG: Renderizando template...")
        
        return render_template('orden-servicio-ver.html', orden=orden)  # ← CAMBIO AQUÍ
        
    except Exception as e:
        print(f"❌ ERROR en ordenes_servicio_ver: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500