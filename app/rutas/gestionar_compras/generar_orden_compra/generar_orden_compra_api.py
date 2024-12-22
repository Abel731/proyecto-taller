from datetime import date
from flask import Blueprint, jsonify, request, current_app as app
from app.dao.gestionar_compras.generar_orden_de_compra.orden_de_compra_dao \
    import OrdenDeCompraDao
from app.dao.gestionar_compras.generar_orden_de_compra.dto.orden_de_compra_dto \
    import OrdenDeCompraDto
from app.dao.gestionar_compras.generar_orden_de_compra.dto.orden_de_compra_det_dto \
    import OrdenDeCompraDetalleDto
from app.dao.referenciales.estado_orden_compra.estado_orden_compra_dto import EstadoOrdenDeCompraDto

odcapi = Blueprint('odcapi', __name__)

ESTADOS_ORDEN = {
    'aprobado': 1,
    'pendiente': 2,
    'rechazado': 3
}

@odcapi.route('/ordenes', methods=['GET'])
def get_ordenes():
    dao = OrdenDeCompraDao()

    try:
        ordenes = dao.obtener_ordenes()
        return jsonify({
            'success': True,
            'data': ordenes,
            'error': False
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener las órdenes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador'
        }), 500

@odcapi.route('/ordenes', methods=['POST'])
def add_orden():
    odcdao = OrdenDeCompraDao()
    data = request.get_json()
    print(f"Datos recibidos: {data}")

    # Validar campos requeridos para la cabecera
    campos_requeridos_cabecera = ['id_empleado', 'id_sucursal', 'fecha_orden', 'detalle_orden', 'id_proveedor', 'estado']
    for campo in campos_requeridos_cabecera:
        if campo not in data or data[campo] is None:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        # Extraer datos de la cabecera
        id_empleado = data['id_empleado']
        id_sucursal = data['id_sucursal']
        fecha_orden = data['fecha_orden']
        id_proveedor = data['id_proveedor']
        detalle_orden = data['detalle_orden']
        estado = data['estado']
        id_presupuesto = data['id_presupuesto']

        # Validar estado
        if estado not in ESTADOS_ORDEN:
            return jsonify({
                'success': False,
                'error': f'El estado {estado} no es válido.'
            }), 400

        # Crear detalle de la orden
        detalle_dto = []
        for item in detalle_orden:
            # Validar campos requeridos en el detalle
            campos_requeridos_detalle = ['id_producto', 'cantidad', 'precio_unitario', 'total']
            for campo in campos_requeridos_detalle:
                if campo not in item or item[campo] is None:
                    return jsonify({
                        'success': False,
                        'error': f'El campo {campo} es obligatorio en el detalle y no puede estar vacío.'
                    }), 400

            # Crear el DTO del detalle
            detalle_dto.append(OrdenDeCompraDetalleDto(
                id_producto=item['id_producto'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario'],
                total_producto=item['total']  
            ))

        # Crear DTO de la cabecera de la orden
        cabecera_dto = OrdenDeCompraDto(
            id_orden=None,                
            id_proveedor=id_proveedor,    
            id_presupuesto=id_presupuesto,  
            id_empleado=id_empleado,      
            id_sucursal=id_sucursal,      
            estado=EstadoOrdenDeCompraDto(id=ESTADOS_ORDEN[estado], descripcion=None),  
            fecha_orden=date.fromisoformat(fecha_orden), 
            detalle_orden=detalle_dto     
        )

        # Registrar orden en la base de datos
        resultado = odcdao.agregar(orden_dto=cabecera_dto)
        if resultado:
            return jsonify({
                'success': True,
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo crear la orden. Consulte con el administrador.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al crear orden: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
