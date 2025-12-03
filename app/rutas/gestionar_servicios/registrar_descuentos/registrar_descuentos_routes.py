from flask import Blueprint, render_template, redirect, url_for
from app.dao.gestionar_servicios.registrar_descuentos.registrar_descuentos_dao import DescuentoDao
import json

# Crear Blueprint para las vistas HTML
descuentomod = Blueprint('descuentomod', __name__, template_folder='templates')

# ========================================================================
# RUTAS - DESCUENTOS
# ========================================================================

# ========== RUTA 1: INDEX (Listado) ==========
@descuentomod.route('/descuentos')
def descuentos_index():
    """
    Muestra el listado de todos los descuentos
    """
    try:
        print("========== DEBUG ROUTE: Cargando index de descuentos ==========")
        return render_template('descuento-index.html')
        
    except Exception as e:
        print(f"❌ ERROR en descuentos_index: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 2: GESTION (Registrar) ==========
@descuentomod.route('/descuentos-gestion')
def descuentos_gestion():
    """
    Muestra el formulario para registrar un nuevo descuento
    """
    try:
        print("========== DEBUG ROUTE: Iniciando carga de datos para descuento ==========")
        
        dao = DescuentoDao()
        
        # Obtener tipos de descuento
        print("DEBUG: Obteniendo tipos de descuento...")
        tipos_descuento = dao.obtener_tipos_descuento()
        
        # Obtener productos
        print("DEBUG: Obteniendo productos...")
        productos = dao.obtener_productos()
        
        # Convertir productos a JSON para JavaScript
        productos_json = json.dumps(productos)
        
        print(f"DEBUG: Tipos de descuento: {len(tipos_descuento)}")
        print(f"DEBUG: Productos: {len(productos)}")
        print("DEBUG: Renderizando template...")
        
        return render_template(
            'descuento-gestion.html',
            tipos_descuento=tipos_descuento,
            productos_json=productos_json
        )
        
    except Exception as e:
        print(f"❌ ERROR en descuentos_gestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 3: VER DETALLE ==========
@descuentomod.route('/descuentos-ver/<int:id_descuento>')
def descuentos_ver(id_descuento):
    """
    Muestra el detalle de un descuento específico
    """
    try:
        print(f"========== DEBUG ROUTE: Cargando detalle de descuento {id_descuento} ==========")
        
        dao = DescuentoDao()
        descuento = dao.obtener_por_id(id_descuento)
        
        if not descuento:
            print(f"DEBUG: Descuento {id_descuento} no encontrado")
            return redirect(url_for('descuentomod.descuentos_index'))
        
        print(f"DEBUG: Descuento encontrado - Estado: {descuento['estado_vigencia']}")
        print("DEBUG: Renderizando template...")
        
        return render_template('descuento-ver.html', descuento=descuento)
        
    except Exception as e:
        print(f"❌ ERROR en descuentos_ver: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500
