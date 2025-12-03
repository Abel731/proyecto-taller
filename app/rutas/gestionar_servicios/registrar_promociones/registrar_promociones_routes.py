from flask import Blueprint, render_template, redirect, url_for
from app.dao.gestionar_servicios.registrar_promociones.registrar_promociones_dao import PromocionDao
import json

# Crear Blueprint para las vistas HTML
promocionmod = Blueprint('promocionmod', __name__, template_folder='templates')

# ========================================================================
# RUTAS - PROMOCIONES
# ========================================================================

# ========== RUTA 1: INDEX (Listado) ==========
@promocionmod.route('/promociones')
def promociones_index():
    """
    Muestra el listado de todas las promociones
    """
    try:
        print("========== DEBUG ROUTE: Cargando index de promociones ==========")
        return render_template('promocion-index.html')
        
    except Exception as e:
        print(f"❌ ERROR en promociones_index: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 2: GESTION (Registrar) ==========
@promocionmod.route('/promociones-gestion')
def promociones_gestion():
    """
    Muestra el formulario para registrar una nueva promoción
    """
    try:
        print("========== DEBUG ROUTE: Iniciando carga de datos para promoción ==========")
        
        dao = PromocionDao()
        
        # Obtener tipos de promoción
        print("DEBUG: Obteniendo tipos de promoción...")
        tipos_promocion = dao.obtener_tipos_promocion()
        
        # Obtener productos
        print("DEBUG: Obteniendo productos...")
        productos = dao.obtener_productos()
        
        # Convertir productos a JSON para JavaScript
        productos_json = json.dumps(productos)
        
        print(f"DEBUG: Tipos de promoción: {len(tipos_promocion)}")
        print(f"DEBUG: Productos: {len(productos)}")
        print("DEBUG: Renderizando template...")
        
        return render_template(
            'promocion-gestion.html',
            tipos_promocion=tipos_promocion,
            productos_json=productos_json
        )
        
    except Exception as e:
        print(f"❌ ERROR en promociones_gestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 3: VER DETALLE ==========
@promocionmod.route('/promociones-ver/<int:id_promocion>')
def promociones_ver(id_promocion):
    """
    Muestra el detalle de una promoción específica
    """
    try:
        print(f"========== DEBUG ROUTE: Cargando detalle de promoción {id_promocion} ==========")
        
        dao = PromocionDao()
        promocion = dao.obtener_por_id(id_promocion)
        
        if not promocion:
            print(f"DEBUG: Promoción {id_promocion} no encontrada")
            return redirect(url_for('promocionmod.promociones_index'))
        
        print(f"DEBUG: Promoción encontrada - Estado: {promocion['estado_vigencia']}")
        print("DEBUG: Renderizando template...")
        
        return render_template('promocion-ver.html', promocion=promocion)
        
    except Exception as e:
        print(f"❌ ERROR en promociones_ver: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500