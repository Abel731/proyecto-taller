from flask import Blueprint, request, jsonify
from app.dao.gestionar_servicios.registrar_ajustes.registrar_ajustes_dao import AjusteStockDao

# Crear Blueprint
ajusteapi = Blueprint('ajusteapi', __name__)

#  ENDPOINT 1: OBTENER TODOS LOS AJUSTES 
@ajusteapi.route('/ajustes', methods=['GET'])
def obtener_ajustes():
    """
    GET /api/v1/gestionar-servicios/registrar-ajustes/ajustes
    Retorna todos los ajustes registrados
    """
    try:
        dao = AjusteStockDao()
        ajustes = dao.obtener_todos()
        
        return jsonify({
            'success': True,
            'data': ajustes,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_ajustes: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener ajustes: {str(e)}'
        }), 500


#  ENDPOINT 2: OBTENER AJUSTE POR ID 
@ajusteapi.route('/ajustes/<int:id_ajuste>', methods=['GET'])
def obtener_ajuste_por_id(id_ajuste):
    """
    GET /api/v1/gestionar-servicios/registrar-ajustes/ajustes/<id>
    Retorna un ajuste específico con su detalle
    """
    try:
        dao = AjusteStockDao()
        ajuste = dao.obtener_por_id(id_ajuste)
        
        if ajuste:
            return jsonify({
                'success': True,
                'data': ajuste,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el ajuste N° {id_ajuste}'
            }), 404
            
    except Exception as e:
        print(f"❌ ERROR en obtener_ajuste_por_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener el ajuste: {str(e)}'
        }), 500


#  ENDPOINT 3: REGISTRAR NUEVO AJUSTE 
@ajusteapi.route('/ajustes', methods=['POST'])
def registrar_ajuste():
    """
    POST /api/v1/gestionar-servicios/registrar-ajustes/ajustes
    Registra un nuevo ajuste de stock
    """
    try:
        print("========== DEBUG API: Iniciando registro de ajuste ==========")
        
        data = request.get_json()
        print(f"DEBUG API: Data recibida: {data}")
        
        # Validar campos requeridos
        campos_requeridos = [
            'id_empleado', 'id_deposito', 'tipo_ajuste', 
            'fecha_ajuste', 'detalle_ajuste'
        ]
        
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None:
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es obligatorio'
                }), 400
        
        # Validar tipo de ajuste
        if data['tipo_ajuste'] not in ['POSITIVO', 'NEGATIVO']:
            return jsonify({
                'success': False,
                'error': 'El tipo de ajuste debe ser POSITIVO o NEGATIVO'
            }), 400
        
        # Validar que detalle_ajuste no esté vacío
        if not isinstance(data['detalle_ajuste'], list) or len(data['detalle_ajuste']) == 0:
            return jsonify({
                'success': False,
                'error': 'El detalle del ajuste debe contener al menos un producto'
            }), 400
        
        # Validar estructura de cada producto
        for item in data['detalle_ajuste']:
            if 'id_producto' not in item or 'cantidad' not in item or 'id_motivo_ajuste' not in item:
                return jsonify({
                    'success': False,
                    'error': 'Cada producto debe tener id_producto, cantidad y id_motivo_ajuste'
                }), 400
            
            # Validar que la cantidad sea positiva
            if item['cantidad'] <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Las cantidades deben ser mayores a 0'
                }), 400
        
        # Preparar datos de cabecera
        datos_ajuste = {
            'id_empleado': data['id_empleado'],
            'id_deposito': data['id_deposito'],
            'tipo_ajuste': data['tipo_ajuste'],
            'fecha_ajuste': data['fecha_ajuste'],
            'observacion': data.get('observacion', None)
        }
        
        print("DEBUG API: Datos de ajuste preparados:")
        print(datos_ajuste)
        print("DEBUG API: Detalle de ajuste:")
        print(data['detalle_ajuste'])
        
        # Registrar el ajuste
        print("DEBUG API: Llamando a agregar_ajuste()...")
        dao = AjusteStockDao()
        id_ajuste = dao.agregar_ajuste(datos_ajuste, data['detalle_ajuste'])
        
        if id_ajuste:
            print(f"DEBUG API: Ajuste registrado exitosamente. ID: {id_ajuste}")
            return jsonify({
                'success': True,
                'mensaje': f'Ajuste N° {id_ajuste} registrado exitosamente',
                'id_ajuste': id_ajuste
            }), 201
        else:
            print("DEBUG API: Error al registrar ajuste (DAO retornó None)")
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar el ajuste. Consulte con el administrador'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación en registrar_ajuste API: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en registrar_ajuste API: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al procesar la solicitud: {str(e)}'
        }), 500


#  ENDPOINT 4: ANULAR AJUSTE 
@ajusteapi.route('/ajustes/<int:id_ajuste>/anular', methods=['PUT'])
def anular_ajuste(id_ajuste):
    """
    PUT /api/v1/gestionar-servicios/registrar-ajustes/ajustes/<id>/anular
    Anula un ajuste y revierte los cambios en el stock
    """
    try:
        print(f"========== DEBUG API: Anulando ajuste {id_ajuste} ==========")
        
        dao = AjusteStockDao()
        
        # Verificar que el ajuste existe
        ajuste = dao.obtener_por_id(id_ajuste)
        if not ajuste:
            return jsonify({
                'success': False,
                'error': f'No se encontró el ajuste N° {id_ajuste}'
            }), 404
        
        # Verificar que no esté ya anulado
        if ajuste['id_estado_ajuste'] == 2:
            return jsonify({
                'success': False,
                'error': 'Este ajuste ya está anulado'
            }), 400
        
        # Anular el ajuste
        if dao.anular_ajuste(id_ajuste):
            print(f"DEBUG API: Ajuste {id_ajuste} anulado exitosamente")
            return jsonify({
                'success': True,
                'mensaje': f'Ajuste N° {id_ajuste} anulado exitosamente'
            }), 200
        else:
            print(f"DEBUG API: No se pudo anular ajuste {id_ajuste}")
            return jsonify({
                'success': False,
                'error': 'No se pudo anular el ajuste'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación en anular_ajuste API: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en anular_ajuste API: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al anular el ajuste: {str(e)}'
        }), 500


#  ENDPOINT 5: OBTENER PRODUCTOS DISPONIBLES 
@ajusteapi.route('/productos', methods=['GET'])
def obtener_productos():
    """
    GET /api/v1/gestionar-servicios/registrar-ajustes/productos
    Retorna todos los productos activos
    """
    try:
        dao = AjusteStockDao()
        productos = dao.obtener_productos_disponibles()
        
        return jsonify({
            'success': True,
            'data': productos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_productos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener productos: {str(e)}'
        }), 500


#  ENDPOINT 6: OBTENER MOTIVOS DE AJUSTE 
@ajusteapi.route('/motivos', methods=['GET'])
def obtener_motivos():
    """
    GET /api/v1/gestionar-servicios/registrar-ajustes/motivos
    Retorna todos los motivos de ajuste
    """
    try:
        dao = AjusteStockDao()
        motivos = dao.obtener_motivos()
        
        return jsonify({
            'success': True,
            'data': motivos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_motivos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener motivos: {str(e)}'
        }), 500


#  ENDPOINT 7: OBTENER DEPÓSITOS 
@ajusteapi.route('/depositos', methods=['GET'])
def obtener_depositos():
    """
    GET /api/v1/gestionar-servicios/registrar-ajustes/depositos
    Retorna todos los depósitos activos
    """
    try:
        dao = AjusteStockDao()
        con = dao.conexion.getConexion()
        cursor = con.cursor()
        
        query = """
        SELECT id_deposito, descripcion
        FROM depositos
        WHERE estado = TRUE
        ORDER BY descripcion
        """
        
        cursor.execute(query)
        depositos = cursor.fetchall()
        
        lista_depositos = []
        for dep in depositos:
            lista_depositos.append({
                'id_deposito': dep[0],
                'descripcion': dep[1]
            })
        
        cursor.close()
        con.close()
        
        return jsonify({
            'success': True,
            'data': lista_depositos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_depositos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener depósitos: {str(e)}'
        }), 500