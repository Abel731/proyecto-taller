from flask import Blueprint, render_template, redirect, url_for
from app.dao.gestionar_servicios.registrar_solicitud_servicio.registrar_solicitud_servicio_dao import SolicitudServicioDao
from app.conexion.Conexion import Conexion
# Crear Blueprint para las vistas HTML
solicitudmod = Blueprint('solicitudmod', __name__, template_folder='templates')

# ========================================================================
# RUTAS - SOLICITUD DE SERVICIO
# ========================================================================

# ========== RUTA 1: INDEX (Listado) ==========
@solicitudmod.route('/solicitudes')
def solicitudes_index():
    """
    Muestra el listado de todas las solicitudes de servicio
    """
    try:
        print("========== DEBUG ROUTE: Cargando index de solicitudes ==========")
        return render_template('solicitud-index.html')
        
    except Exception as e:
        print(f"❌ ERROR en solicitudes_index: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 2: GESTION (Registrar) ==========
@solicitudmod.route('/solicitudes-gestion')
def solicitudes_gestion():
    """
    Muestra el formulario para registrar una nueva solicitud de servicio
    """
    try:
        print("========== DEBUG ROUTE: Iniciando carga de datos para solicitud ==========")
        
        dao = SolicitudServicioDao()
        
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
        
        # ========== OBTENER CLIENTES, TIPOS DE SERVICIO Y PRODUCTOS (cada uno con su conexión) ==========
        print("DEBUG: Obteniendo clientes, tipos de servicio y productos...")
        clientes = dao.obtener_clientes()
        tipos_servicio = dao.obtener_tipos_servicio()
        productos = dao.obtener_productos()
        
        print(f"DEBUG: Clientes: {len(clientes)}")
        print(f"DEBUG: Tipos de servicio: {len(tipos_servicio)}")
        print(f"DEBUG: Productos: {len(productos)}")
        print("DEBUG: Renderizando template...")
        
        return render_template(
            'solicitud-gestion.html',
            empleados=empleados,
            clientes=clientes,
            tipos_servicio=tipos_servicio,
            productos=productos
        )
        
    except Exception as e:
        print(f"❌ ERROR en solicitudes_gestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 3: VER DETALLE ==========
@solicitudmod.route('/solicitudes-ver/<int:id_solicitud>')
def solicitudes_ver(id_solicitud):
    """
    Muestra el detalle de una solicitud de servicio específica
    """
    try:
        print(f"========== DEBUG ROUTE: Cargando detalle de solicitud {id_solicitud} ==========")
        
        dao = SolicitudServicioDao()
        solicitud = dao.obtener_por_id(id_solicitud)
        
        if not solicitud:
            print(f"DEBUG: Solicitud {id_solicitud} no encontrada")
            return redirect(url_for('solicitudmod.solicitudes_index'))
        
        print(f"DEBUG: Solicitud encontrada - Estado: {solicitud['estado']}")
        print("DEBUG: Renderizando template...")
        
        return render_template('solicitud-ver.html', solicitud=solicitud)
        
    except Exception as e:
        print(f"❌ ERROR en solicitudes_ver: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500