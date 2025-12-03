from flask import Blueprint, request, jsonify
from app.dao.gestionar_compras.registrar_nota_compra.registrar_nota_compra_dao import NotasCompraDao

# Crear Blueprint
notasapi = Blueprint('notasapi', __name__)

# ========================================================================
# ENDPOINTS - NOTAS DE CRÉDITO
# ========================================================================

# ========== ENDPOINT 1: OBTENER TODAS LAS NC ==========
@notasapi.route('/notas-credito', methods=['GET'])
def obtener_notas_credito():
    """
    GET /api/v1/gestionar-compras/registrar-notas/notas-credito
    Retorna todas las notas de crédito registradas
    """
    try:
        dao = NotasCompraDao()
        notas = dao.obtener_todas_nc()
        
        return jsonify({
            'success': True,
            'data': notas,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_notas_credito: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener notas de crédito: {str(e)}'
        }), 500


# ========== ENDPOINT 2: OBTENER NC POR ID ==========
@notasapi.route('/notas-credito/<int:id_nota_credito>', methods=['GET'])
def obtener_nota_credito_por_id(id_nota_credito):
    """
    GET /api/v1/gestionar-compras/registrar-notas/notas-credito/<id>
    Retorna una nota de crédito específica con su detalle
    """
    try:
        dao = NotasCompraDao()
        nota = dao.obtener_nc_por_id(id_nota_credito)
        
        if nota:
            return jsonify({
                'success': True,
                'data': nota,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la NC N° {id_nota_credito}'
            }), 404
            
    except Exception as e:
        print(f"❌ ERROR en obtener_nota_credito_por_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener la nota de crédito: {str(e)}'
        }), 500


# ========== ENDPOINT 3: REGISTRAR NUEVA NC ==========
@notasapi.route('/notas-credito', methods=['POST'])
def registrar_nota_credito():
    """
    POST /api/v1/gestionar-compras/registrar-notas/notas-credito
    Registra una nueva nota de crédito
    """
    try:
        print("========== DEBUG API: Iniciando registro de NC ==========")
        
        data = request.get_json()
        print(f"DEBUG API: Data recibida: {data}")
        
        # Validar campos requeridos
        campos_requeridos = [
            'id_compra', 'id_proveedor', 'id_empleado', 'id_deposito',
            'nro_nota_credito', 'timbrado', 'fecha_emision', 
            'fecha_vencimiento_timbrado', 'id_motivo_nc', 'detalle_nc'
        ]
        
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None:
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es obligatorio'
                }), 400
        
        # Validar formato de número de NC
        import re
        if not re.match(r'^\d{3}-\d{3}-\d{7}$', data['nro_nota_credito']):
            return jsonify({
                'success': False,
                'error': 'El número de NC debe tener el formato XXX-XXX-XXXXXXX'
            }), 400
        
        # Validar formato de timbrado
        if not re.match(r'^\d{8}$', data['timbrado']):
            return jsonify({
                'success': False,
                'error': 'El timbrado debe tener 8 dígitos numéricos'
            }), 400
        
        # Validar detalle
        if not isinstance(data['detalle_nc'], list) or len(data['detalle_nc']) == 0:
            return jsonify({
                'success': False,
                'error': 'El detalle debe contener al menos un producto'
            }), 400
        
        for item in data['detalle_nc']:
            if 'id_producto' not in item or 'cantidad' not in item or 'precio_unitario' not in item or 'id_impuesto' not in item:
                return jsonify({
                    'success': False,
                    'error': 'Cada producto debe tener id_producto, cantidad, precio_unitario e id_impuesto'
                }), 400
        
        # Preparar datos
        datos_nc = {
            'id_compra': data['id_compra'],
            'id_proveedor': data['id_proveedor'],
            'id_empleado': data['id_empleado'],
            'id_deposito': data['id_deposito'],
            'nro_nota_credito': data['nro_nota_credito'],
            'timbrado': data['timbrado'],
            'fecha_emision': data['fecha_emision'],
            'fecha_vencimiento_timbrado': data['fecha_vencimiento_timbrado'],
            'id_motivo_nc': data['id_motivo_nc'],
            'observacion': data.get('observacion', None)
        }
        
        # Registrar NC
        dao = NotasCompraDao()
        id_nota_credito = dao.agregar_nota_credito(datos_nc, data['detalle_nc'])
        
        if id_nota_credito:
            print(f"DEBUG API: NC registrada exitosamente. ID: {id_nota_credito}")
            return jsonify({
                'success': True,
                'mensaje': f'Nota de Crédito N° {id_nota_credito} registrada exitosamente',
                'id_nota_credito': id_nota_credito
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar la nota de crédito'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en registrar_nota_credito: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al procesar la solicitud: {str(e)}'
        }), 500


# ========== ENDPOINT 4: ANULAR NC ==========
@notasapi.route('/notas-credito/<int:id_nota_credito>/anular', methods=['PUT'])
def anular_nota_credito(id_nota_credito):
    """
    PUT /api/v1/gestionar-compras/registrar-notas/notas-credito/<id>/anular
    Anula una nota de crédito
    """
    try:
        print(f"========== DEBUG API: Anulando NC {id_nota_credito} ==========")
        
        dao = NotasCompraDao()
        
        if dao.anular_nota_credito(id_nota_credito):
            print(f"DEBUG API: NC {id_nota_credito} anulada exitosamente")
            return jsonify({
                'success': True,
                'mensaje': f'Nota de Crédito N° {id_nota_credito} anulada exitosamente'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo anular la nota de crédito'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en anular_nota_credito: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al anular la nota de crédito: {str(e)}'
        }), 500


# ========================================================================
# ENDPOINTS - NOTAS DE DÉBITO
# ========================================================================

# ========== ENDPOINT 5: OBTENER TODAS LAS ND ==========
@notasapi.route('/notas-debito', methods=['GET'])
def obtener_notas_debito():
    """
    GET /api/v1/gestionar-compras/registrar-notas/notas-debito
    Retorna todas las notas de débito registradas
    """
    try:
        dao = NotasCompraDao()
        notas = dao.obtener_todas_nd()
        
        return jsonify({
            'success': True,
            'data': notas,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_notas_debito: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener notas de débito: {str(e)}'
        }), 500


# ========== ENDPOINT 6: OBTENER ND POR ID ==========
@notasapi.route('/notas-debito/<int:id_nota_debito>', methods=['GET'])
def obtener_nota_debito_por_id(id_nota_debito):
    """
    GET /api/v1/gestionar-compras/registrar-notas/notas-debito/<id>
    Retorna una nota de débito específica con su detalle
    """
    try:
        dao = NotasCompraDao()
        nota = dao.obtener_nd_por_id(id_nota_debito)
        
        if nota:
            return jsonify({
                'success': True,
                'data': nota,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la ND N° {id_nota_debito}'
            }), 404
            
    except Exception as e:
        print(f"❌ ERROR en obtener_nota_debito_por_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener la nota de débito: {str(e)}'
        }), 500


# ========== ENDPOINT 7: REGISTRAR NUEVA ND ==========
@notasapi.route('/notas-debito', methods=['POST'])
def registrar_nota_debito():
    """
    POST /api/v1/gestionar-compras/registrar-notas/notas-debito
    Registra una nueva nota de débito
    """
    try:
        print("========== DEBUG API: Iniciando registro de ND ==========")
        
        data = request.get_json()
        print(f"DEBUG API: Data recibida: {data}")
        
        # Validar campos requeridos
        campos_requeridos = [
            'id_compra', 'id_proveedor', 'id_empleado',
            'nro_nota_debito', 'timbrado', 'fecha_emision', 
            'fecha_vencimiento_timbrado', 'id_motivo_nd', 
            'afecta_stock', 'detalle_nd'
        ]
        
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es obligatorio'
                }), 400
        
        # Si afecta stock, validar depósito
        if data['afecta_stock'] and not data.get('id_deposito'):
            return jsonify({
                'success': False,
                'error': 'Si afecta stock, debe especificar un depósito'
            }), 400
        
        # Validar formato de número de ND
        import re
        if not re.match(r'^\d{3}-\d{3}-\d{7}$', data['nro_nota_debito']):
            return jsonify({
                'success': False,
                'error': 'El número de ND debe tener el formato XXX-XXX-XXXXXXX'
            }), 400
        
        # Validar formato de timbrado
        if not re.match(r'^\d{8}$', data['timbrado']):
            return jsonify({
                'success': False,
                'error': 'El timbrado debe tener 8 dígitos numéricos'
            }), 400
        
        # Validar detalle
        if not isinstance(data['detalle_nd'], list) or len(data['detalle_nd']) == 0:
            return jsonify({
                'success': False,
                'error': 'El detalle debe contener al menos un item'
            }), 400
        
        for item in data['detalle_nd']:
            if 'id_producto' not in item or 'cantidad' not in item or 'precio_unitario' not in item or 'id_impuesto' not in item:
                return jsonify({
                    'success': False,
                    'error': 'Cada item debe tener id_producto, cantidad, precio_unitario e id_impuesto'
                }), 400
        
        # Preparar datos
        datos_nd = {
            'id_compra': data['id_compra'],
            'id_proveedor': data['id_proveedor'],
            'id_empleado': data['id_empleado'],
            'id_deposito': data.get('id_deposito', None),
            'nro_nota_debito': data['nro_nota_debito'],
            'timbrado': data['timbrado'],
            'fecha_emision': data['fecha_emision'],
            'fecha_vencimiento_timbrado': data['fecha_vencimiento_timbrado'],
            'id_motivo_nd': data['id_motivo_nd'],
            'afecta_stock': data['afecta_stock'],
            'observacion': data.get('observacion', None)
        }
        
        # Registrar ND
        dao = NotasCompraDao()
        id_nota_debito = dao.agregar_nota_debito(datos_nd, data['detalle_nd'])
        
        if id_nota_debito:
            print(f"DEBUG API: ND registrada exitosamente. ID: {id_nota_debito}")
            return jsonify({
                'success': True,
                'mensaje': f'Nota de Débito N° {id_nota_debito} registrada exitosamente',
                'id_nota_debito': id_nota_debito
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar la nota de débito'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en registrar_nota_debito: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al procesar la solicitud: {str(e)}'
        }), 500


# ========== ENDPOINT 8: ANULAR ND ==========
@notasapi.route('/notas-debito/<int:id_nota_debito>/anular', methods=['PUT'])
def anular_nota_debito(id_nota_debito):
    """
    PUT /api/v1/gestionar-compras/registrar-notas/notas-debito/<id>/anular
    Anula una nota de débito
    """
    try:
        print(f"========== DEBUG API: Anulando ND {id_nota_debito} ==========")
        
        dao = NotasCompraDao()
        
        if dao.anular_nota_debito(id_nota_debito):
            print(f"DEBUG API: ND {id_nota_debito} anulada exitosamente")
            return jsonify({
                'success': True,
                'mensaje': f'Nota de Débito N° {id_nota_debito} anulada exitosamente'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo anular la nota de débito'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en anular_nota_debito: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al anular la nota de débito: {str(e)}'
        }), 500


# ========================================================================
# ENDPOINTS AUXILIARES
# ========================================================================

# ========== ENDPOINT 9: OBTENER COMPRAS DISPONIBLES ==========
@notasapi.route('/compras-disponibles', methods=['GET'])
def obtener_compras_disponibles():
    """
    GET /api/v1/gestionar-compras/registrar-notas/compras-disponibles
    Retorna compras finalizadas que pueden tener notas
    """
    try:
        dao = NotasCompraDao()
        compras = dao.obtener_compras_finalizadas()
        
        return jsonify({
            'success': True,
            'data': compras,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_compras_disponibles: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener compras: {str(e)}'
        }), 500


# ========== ENDPOINT 10: OBTENER PRODUCTOS DE COMPRA ==========
@notasapi.route('/compras/<int:id_compra>/productos', methods=['GET'])
def obtener_productos_compra(id_compra):
    """
    GET /api/v1/gestionar-compras/registrar-notas/compras/<id>/productos
    Retorna los productos de una compra
    """
    try:
        dao = NotasCompraDao()
        productos = dao.obtener_productos_compra(id_compra)
        
        return jsonify({
            'success': True,
            'data': productos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_productos_compra: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener productos: {str(e)}'
        }), 500


# ========== ENDPOINT 11: OBTENER MOTIVOS NC ==========
@notasapi.route('/motivos-nc', methods=['GET'])
def obtener_motivos_nc():
    """
    GET /api/v1/gestionar-compras/registrar-notas/motivos-nc
    Retorna motivos de nota de crédito
    """
    try:
        dao = NotasCompraDao()
        motivos = dao.obtener_motivos_nc()
        
        return jsonify({
            'success': True,
            'data': motivos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_motivos_nc: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener motivos: {str(e)}'
        }), 500


# ========== ENDPOINT 12: OBTENER MOTIVOS ND ==========
@notasapi.route('/motivos-nd', methods=['GET'])
def obtener_motivos_nd():
    """
    GET /api/v1/gestionar-compras/registrar-notas/motivos-nd
    Retorna motivos de nota de débito
    """
    try:
        dao = NotasCompraDao()
        motivos = dao.obtener_motivos_nd()
        
        return jsonify({
            'success': True,
            'data': motivos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_motivos_nd: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener motivos: {str(e)}'
        }), 500