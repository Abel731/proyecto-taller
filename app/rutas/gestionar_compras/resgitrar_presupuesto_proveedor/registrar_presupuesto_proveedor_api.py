from datetime import date
from flask import Blueprint, jsonify, request, current_app as app
from app.dao.gestionar_compras.registrar_presupuesto_proveedor.presupuesto_de_proveedor_dao \
    import PresupuestoProvDao

from app.dao.gestionar_compras.registrar_presupuesto_proveedor.dto.presupuesto_prov_detalle_dto \
    import PresupuestoProvDetalleDto

from app.dao.referenciales.estado_presupuesto_proveedor.estado_presupuesto_proveedor_dto \
    import  EstadoPresupuestoProveedor

from app.dao.gestionar_compras.registrar_presupuesto_proveedor.dto.presupuesto_prov_dto \
    import PresupuestoProvDto

pdpapi = Blueprint('pdpapi', __name__)

@pdpapi.route('/presupuestos', methods=['GET'])
def get_presupuestos():
    dao = PresupuestoProvDao()

    try:
        presupuestos = dao.obtener_presupuestos()
        return jsonify({
            'success': True,
            'data': presupuestos,
            'error': False
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener los presupuestos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador'
        }), 500

@pdpapi.route('/presupuestos', methods=['POST'])
def add_presupuesto():
    ppdao = PresupuestoProvDao()
    data = request.get_json()

    # Validar campos requeridos
    campos_requeridos = ['id_empleado', 'id_sucursal', 'fecha_presupuesto', 'detalle_presupuesto', 'id_proveedor', 'id_pedido_compra']
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        # Extraer datos
        id_empleado = data['id_empleado']
        id_sucursal = data['id_sucursal']
        fecha_presupuesto = data['fecha_presupuesto']
        id_proveedor = data['id_proveedor']
        id_pedido_compra = data['id_pedido_compra']
        detalle_presupuesto = data['detalle_presupuesto']

        # Crear detalle del presupuesto
        detalle_dto = [
            PresupuestoProvDetalleDto(
                id_producto=item['id_producto'],
                cantidad=item['cantidad'],
                precio_unitario=item.get('precio', 0)
            ) for item in detalle_presupuesto
        ]

        # Crear cabecera del presupuesto 
        cabecera_dto = PresupuestoProvDto(
            id_presupuesto=None,
            id_empleado=id_empleado,
            id_sucursal=id_sucursal,
            id_proveedor=id_proveedor,  
            id_pedido_compra=id_pedido_compra,  
            estado=EstadoPresupuestoProveedor(id=2, descripcion=None),
            fecha_presupuesto=date.fromisoformat(fecha_presupuesto),
            detalle_presupuesto=detalle_dto
        )

        # Registrar presupuesto en la base de datos
        resultado = ppdao.agregar(presupuesto_dto=cabecera_dto)
        if resultado:
            return jsonify({
                'success': True,
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo crear el presupuesto. Consulte con el administrador.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al crear presupuesto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500