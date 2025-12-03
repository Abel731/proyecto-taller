from flask import Blueprint, render_template, redirect, url_for
from app.dao.gestionar_servicios.registrar_presupuesto_servicio.registrar_presupuesto_servicio_dao import PresupuestoServicioDao
from app.conexion.Conexion import Conexion
import json

# Crear Blueprint para las vistas HTML
presupuestomod = Blueprint('presupuestomod', __name__, template_folder='templates')

# ========================================================================
# RUTAS - PRESUPUESTO DE SERVICIO
# ========================================================================

# ========== RUTA 1: INDEX (Listado) ==========
@presupuestomod.route('/presupuestos')
def presupuestos_index():
    """
    Muestra el listado de todos los presupuestos de servicio
    """
    try:
        print("========== DEBUG ROUTE: Cargando index de presupuestos ==========")
        return render_template('presupuesto-index.html')
        
    except Exception as e:
        print(f"❌ ERROR en presupuestos_index: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 2: GESTION (Registrar) ==========
@presupuestomod.route('/presupuestos-gestion')
def presupuestos_gestion():
    """
    Muestra el formulario para registrar un nuevo presupuesto de servicio
    """
    try:
        print("========== DEBUG ROUTE: Iniciando carga de datos para presupuesto ==========")
        
        dao = PresupuestoServicioDao()
        
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
        
        # ========== OBTENER SOLICITUDES FINALIZADAS E IMPUESTOS (cada uno con su conexión) ==========
        print("DEBUG: Obteniendo solicitudes finalizadas e impuestos...")
        solicitudes_disponibles = dao.obtener_solicitudes_finalizadas()
        impuestos = dao.obtener_impuestos()
        
        print(f"DEBUG: Solicitudes disponibles: {len(solicitudes_disponibles)}")
        print(f"DEBUG: Impuestos: {len(impuestos)}")
        
        # Convertir impuestos a JSON para usar en JavaScript
        impuestos_json = json.dumps(impuestos)
        
        print("DEBUG: Renderizando template...")
        
        return render_template(
            'presupuesto-gestion.html',
            empleados=empleados,
            solicitudes_disponibles=solicitudes_disponibles,
            impuestos_json=impuestos_json
        )
        
    except Exception as e:
        print(f"❌ ERROR en presupuestos_gestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 3: VER DETALLE ==========
@presupuestomod.route('/presupuestos-ver/<int:id_presupuesto>')
def presupuestos_ver(id_presupuesto):
    """
    Muestra el detalle de un presupuesto de servicio específico
    """
    try:
        print(f"========== DEBUG ROUTE: Cargando detalle de presupuesto {id_presupuesto} ==========")
        
        dao = PresupuestoServicioDao()
        presupuesto = dao.obtener_por_id(id_presupuesto)
        
        if not presupuesto:
            print(f"DEBUG: Presupuesto {id_presupuesto} no encontrado")
            return redirect(url_for('presupuestomod.presupuestos_index'))
        
        print(f"DEBUG: Presupuesto encontrado - Estado: {presupuesto['estado']}")
        print("DEBUG: Renderizando template...")
        
        return render_template('presupuesto-ver.html', presupuesto=presupuesto)
        
    except Exception as e:
        print(f"❌ ERROR en presupuestos_ver: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500