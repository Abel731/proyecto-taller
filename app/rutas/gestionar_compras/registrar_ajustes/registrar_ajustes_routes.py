from flask import Blueprint, render_template, redirect, url_for
from app.dao.gestionar_compras.registrar_ajustes.registrar_ajustes_dao import AjusteStockDao

# Crear Blueprint para las vistas HTML
ajustemod = Blueprint('ajustemod', __name__, template_folder='templates')

# ========== RUTA 1: INDEX (Listado de ajustes) ==========
@ajustemod.route('/ajustes')
def ajustes_index():
    """
    Muestra el listado de todos los ajustes
    """
    try:
        print("========== DEBUG ROUTE: Cargando index de ajustes ==========")
        return render_template('ajuste-index.html')
        
    except Exception as e:
        print(f"❌ ERROR en ajustes_index: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 2: GESTION (Registrar nuevo ajuste) ==========
@ajustemod.route('/ajustes-gestion')
def ajustes_gestion():
    """
    Muestra el formulario para registrar un nuevo ajuste
    """
    try:
        print("========== DEBUG ROUTE: Iniciando carga de datos para gestión ==========")
        
        dao = AjusteStockDao()
        con = dao.conexion.getConexion()
        cursor = con.cursor()
        
        # Obtener empleados
        print("DEBUG: Ejecutando query empleados...")
        query_empleados = """
        SELECT e.id_empleado, CONCAT(p.nombres, ' ', p.apellidos) AS empleado, p.ci
        FROM empleados e
        INNER JOIN personas p ON e.id_empleado = p.id_persona
        ORDER BY p.apellidos, p.nombres
        """
        cursor.execute(query_empleados)
        empleados_data = cursor.fetchall()
        
        empleados = []
        for emp in empleados_data:
            empleados.append({
                'id_empleado': emp[0],
                'empleado': emp[1],
                'ci': emp[2]
            })
        
        print(f"DEBUG: Empleados encontrados: {len(empleados)}")
        
        # Obtener depósitos
        print("DEBUG: Ejecutando query depósitos...")
        query_depositos = """
        SELECT id_deposito, descripcion
        FROM depositos
        ORDER BY descripcion
        """
        cursor.execute(query_depositos)
        depositos_data = cursor.fetchall()
        
        depositos = []
        for dep in depositos_data:
            depositos.append({
                'id_deposito': dep[0],
                'descripcion': dep[1]
            })
        
        print(f"DEBUG: Depósitos encontrados: {len(depositos)}")
        
        # Obtener productos
        print("DEBUG: Ejecutando query productos...")
        query_productos = """
        SELECT id_producto, nombre
        FROM productos
        ORDER BY nombre
        """
        cursor.execute(query_productos)
        productos_data = cursor.fetchall()
        
        productos = []
        for prod in productos_data:
            productos.append({
                'id_producto': prod[0],
                'nombre': prod[1]
            })
        
        print(f"DEBUG: Productos encontrados: {len(productos)}")
        
        # Obtener motivos
        print("DEBUG: Ejecutando query motivos...")
        query_motivos = """
        SELECT id_motivo_ajuste, descripcion
        FROM motivo_ajuste
        ORDER BY descripcion
        """
        cursor.execute(query_motivos)
        motivos_data = cursor.fetchall()
        
        motivos = []
        for mot in motivos_data:
            motivos.append({
                'id_motivo_ajuste': mot[0],
                'descripcion': mot[1]
            })
        
        print(f"DEBUG: Motivos encontrados: {len(motivos)}")
        
        # Cerrar conexión
        cursor.close()
        con.close()
        
        print("DEBUG: Renderizando template...")
        
        return render_template(
            'ajuste-gestion.html',
            empleados=empleados,
            depositos=depositos,
            productos=productos,
            motivos=motivos
        )
        
    except Exception as e:
        print(f"❌ ERROR en ajustes_gestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 3: VER DETALLE ==========
@ajustemod.route('/ajustes-ver/<int:id_ajuste>')
def ajustes_ver(id_ajuste):
    """
    Muestra el detalle de un ajuste específico
    """
    try:
        print(f"========== DEBUG ROUTE: Cargando detalle de ajuste {id_ajuste} ==========")
        
        dao = AjusteStockDao()
        ajuste = dao.obtener_por_id(id_ajuste)
        
        if not ajuste:
            print(f"DEBUG: Ajuste {id_ajuste} no encontrado")
            return redirect(url_for('ajustemod.ajustes_index'))
        
        print(f"DEBUG: Ajuste encontrado - Tipo: {ajuste['tipo_ajuste']}, Estado: {ajuste['estado']}")
        print("DEBUG: Renderizando template...")
        
        return render_template('ajuste-ver.html', ajuste=ajuste)
        
    except Exception as e:
        print(f"❌ ERROR en ajustes_ver: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500