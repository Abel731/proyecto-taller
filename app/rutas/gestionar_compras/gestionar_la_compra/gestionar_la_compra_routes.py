from flask import Blueprint, render_template, redirect, url_for, flash
from app.dao.gestionar_compras.gestionar_la_compra.gestionar_la_compra_dao import CompraDao

# Crear Blueprint
compramod = Blueprint('compramod', __name__, template_folder='templates')


# ROUTE 1: LISTADO DE COMPRAS (index)
@compramod.route('/compras-index')
def compras_index():
    """
    Ruta: /gestionar-compras/gestionar-compra/compras-index
    Muestra el listado de todas las compras
    """
    return render_template('compra-index.html')


# ROUTE 2: FORMULARIO PARA REGISTRAR COMPRA
@compramod.route('/compras-gestion')
def compras_gestion():
    """
    Ruta: /gestionar-compras/gestionar-compra/compras-gestion
    Muestra el formulario para registrar una nueva compra
    """
    dao = CompraDao()
    
    try:
        con = dao.conexion.getConexion()
        cursor = con.cursor()
        
        print("========== DEBUG ROUTE: Iniciando carga de datos ==========")
        
        # ===== OBTENER EMPLEADOS =====
        query_empleados = """
        SELECT 
            e.id_empleado,
            CONCAT(p.nombres, ' ', p.apellidos) AS empleado,
            p.ci
        FROM empleados e
        INNER JOIN personas p ON e.id_empleado = p.id_persona
        ORDER BY p.nombres, p.apellidos
        """
        
        print("DEBUG: Ejecutando query empleados...")
        cursor.execute(query_empleados)
        empleados = cursor.fetchall()
        print(f"DEBUG: Empleados encontrados: {len(empleados) if empleados else 0}")
        
        lista_empleados = []
        for emp in empleados:
            lista_empleados.append({
                'id_empleado': emp[0],
                'empleado': emp[1],
                'ci': emp[2]
            })
        
        # ===== OBTENER IMPUESTOS =====
        query_impuestos = """
        SELECT id_impuesto, descripcion, tasa
        FROM impuestos
        WHERE activo = TRUE
        ORDER BY tasa DESC
        """
        
        print("DEBUG: Ejecutando query impuestos...")
        cursor.execute(query_impuestos)
        impuestos = cursor.fetchall()
        print(f"DEBUG: Impuestos encontrados: {len(impuestos) if impuestos else 0}")
        
        lista_impuestos = []
        for imp in impuestos:
            lista_impuestos.append({
                'id_impuesto': imp[0],
                'descripcion': imp[1],
                'tasa': float(imp[2])
            })
        
        print(f"DEBUG: Lista de impuestos: {lista_impuestos}")
        
        cursor.close()
        con.close()
        
        # ===== CONVERTIR A JSON STRING =====
        import json
        impuestos_json = json.dumps(lista_impuestos)
        
        print(f"DEBUG: JSON generado: {impuestos_json}")
        print("DEBUG: Renderizando template...")
        
        return render_template(
            'compra-gestion.html',
            empleados=lista_empleados,
            impuestos_json=impuestos_json
        )
        
    except Exception as e:
        print(f"❌ ERROR en compras_gestion: {str(e)}")
        import traceback
        traceback.print_exc()
        
        flash(f'Error al cargar el formulario: {str(e)}', 'error')
        return redirect(url_for('compramod.compras_index'))


# ROUTE 3: VER DETALLE DE COMPRA

@compramod.route('/compras-ver/<int:id_compra>')
def compras_ver(id_compra):
    """
    Ruta: /gestionar-compras/gestionar-compra/compras-ver/<id>
    Muestra el detalle completo de una compra
    """
    dao = CompraDao()
    compra = dao.obtener_por_id(id_compra)
    
    if not compra:
        flash(f'No se encontró la compra N° {id_compra}', 'error')
        return redirect(url_for('compramod.compras_index'))
    
    return render_template('compra-ver.html', compra=compra)