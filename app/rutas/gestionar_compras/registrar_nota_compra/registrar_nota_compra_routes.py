from flask import Blueprint, render_template, redirect, url_for
from app.dao.gestionar_compras.registrar_nota_compra.registrar_nota_compra_dao import NotasCompraDao

# Crear Blueprint para las vistas HTML
notasmod = Blueprint('notasmod', __name__, template_folder='templates')

# ========================================================================
# RUTAS - NOTAS DE CRÉDITO
# ========================================================================

# ========== RUTA 1: INDEX NC (Listado) ==========
@notasmod.route('/notas-credito')
def notas_credito_index():
    """
    Muestra el listado de todas las notas de crédito
    """
    try:
        print("========== DEBUG ROUTE: Cargando index de NC ==========")
        return render_template('notas-credito-index.html')
        
    except Exception as e:
        print(f"❌ ERROR en notas_credito_index: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 2: GESTION NC (Registrar) ==========
@notasmod.route('/notas-credito-gestion')
def notas_credito_gestion():
    """
    Muestra el formulario para registrar una nueva nota de crédito
    """
    try:
        print("========== DEBUG ROUTE: Iniciando carga de datos para NC ==========")
        
        dao = NotasCompraDao()
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
        
        # Obtener impuestos
        print("DEBUG: Ejecutando query impuestos...")
        query_impuestos = """
        SELECT id_impuesto, descripcion, tasa
        FROM impuestos
        ORDER BY tasa DESC
        """
        cursor.execute(query_impuestos)
        impuestos_data = cursor.fetchall()
        
        impuestos = []
        for imp in impuestos_data:
            impuestos.append({
                'id_impuesto': imp[0],
                'descripcion': imp[1],
                'tasa': float(imp[2])
            })
        
        print(f"DEBUG: Impuestos encontrados: {len(impuestos)}")
        
        cursor.close()
        con.close()
        
        # Obtener motivos NC y compras disponibles usando métodos del DAO
        print("DEBUG: Obteniendo motivos NC y compras...")
        motivos_nc = dao.obtener_motivos_nc()
        compras_disponibles = dao.obtener_compras_finalizadas()
        
        print(f"DEBUG: Motivos NC: {len(motivos_nc)}")
        print(f"DEBUG: Compras disponibles: {len(compras_disponibles)}")
        print("DEBUG: Renderizando template...")
        
        import json
        impuestos_json = json.dumps(impuestos)
        
        return render_template(
            'notas-credito-gestion.html',
            empleados=empleados,
            depositos=depositos,
            motivos_nc=motivos_nc,
            compras_disponibles=compras_disponibles,
            impuestos_json=impuestos_json
        )
        
    except Exception as e:
        print(f"❌ ERROR en notas_credito_gestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 3: VER NC ==========
@notasmod.route('/notas-credito-ver/<int:id_nota_credito>')
def notas_credito_ver(id_nota_credito):
    """
    Muestra el detalle de una nota de crédito específica
    """
    try:
        print(f"========== DEBUG ROUTE: Cargando detalle de NC {id_nota_credito} ==========")
        
        dao = NotasCompraDao()
        nota = dao.obtener_nc_por_id(id_nota_credito)
        
        if not nota:
            print(f"DEBUG: NC {id_nota_credito} no encontrada")
            return redirect(url_for('notasmod.notas_credito_index'))
        
        print(f"DEBUG: NC encontrada - Estado: {nota['estado']}")
        print("DEBUG: Renderizando template...")
        
        return render_template('notas-credito-ver.html', nota=nota)
        
    except Exception as e:
        print(f"❌ ERROR en notas_credito_ver: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========================================================================
# RUTAS - NOTAS DE DÉBITO
# ========================================================================

# ========== RUTA 4: INDEX ND (Listado) ==========
@notasmod.route('/notas-debito')
def notas_debito_index():
    """
    Muestra el listado de todas las notas de débito
    """
    try:
        print("========== DEBUG ROUTE: Cargando index de ND ==========")
        return render_template('notas-debito-index.html')
        
    except Exception as e:
        print(f"❌ ERROR en notas_debito_index: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 5: GESTION ND (Registrar) ==========
@notasmod.route('/notas-debito-gestion')
def notas_debito_gestion():
    """
    Muestra el formulario para registrar una nueva nota de débito
    """
    try:
        print("========== DEBUG ROUTE: Iniciando carga de datos para ND ==========")
        
        dao = NotasCompraDao()
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
        
        # Obtener impuestos
        print("DEBUG: Ejecutando query impuestos...")
        query_impuestos = """
        SELECT id_impuesto, descripcion, tasa
        FROM impuestos
        ORDER BY tasa DESC
        """
        cursor.execute(query_impuestos)
        impuestos_data = cursor.fetchall()
        
        impuestos = []
        for imp in impuestos_data:
            impuestos.append({
                'id_impuesto': imp[0],
                'descripcion': imp[1],
                'tasa': float(imp[2])
            })
        
        print(f"DEBUG: Impuestos encontrados: {len(impuestos)}")
        
        cursor.close()
        con.close()
        
        # Obtener motivos ND y compras disponibles usando métodos del DAO
        print("DEBUG: Obteniendo motivos ND y compras...")
        motivos_nd = dao.obtener_motivos_nd()
        compras_disponibles = dao.obtener_compras_finalizadas()
        
        print(f"DEBUG: Motivos ND: {len(motivos_nd)}")
        print(f"DEBUG: Compras disponibles: {len(compras_disponibles)}")
        print("DEBUG: Renderizando template...")
        
        import json
        impuestos_json = json.dumps(impuestos)
        
        return render_template(
            'notas-debito-gestion.html',
            empleados=empleados,
            depositos=depositos,
            motivos_nd=motivos_nd,
            compras_disponibles=compras_disponibles,
            impuestos_json=impuestos_json
        )
        
    except Exception as e:
        print(f"❌ ERROR en notas_debito_gestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500


# ========== RUTA 6: VER ND ==========
@notasmod.route('/notas-debito-ver/<int:id_nota_debito>')
def notas_debito_ver(id_nota_debito):
    """
    Muestra el detalle de una nota de débito específica
    """
    try:
        print(f"========== DEBUG ROUTE: Cargando detalle de ND {id_nota_debito} ==========")
        
        dao = NotasCompraDao()
        nota = dao.obtener_nd_por_id(id_nota_debito)
        
        if not nota:
            print(f"DEBUG: ND {id_nota_debito} no encontrada")
            return redirect(url_for('notasmod.notas_debito_index'))
        
        print(f"DEBUG: ND encontrada - Estado: {nota['estado']}, Afecta stock: {nota['afecta_stock']}")
        print("DEBUG: Renderizando template...")
        
        return render_template('notas-debito-ver.html', nota=nota)
        
    except Exception as e:
        print(f"❌ ERROR en notas_debito_ver: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar la página: {str(e)}", 500