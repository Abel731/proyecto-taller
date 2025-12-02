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

ESTADOS_PRESUPUESTO = {
    'aprobado': 1,
    'pendiente': 2,
    'rechazado': 3
}

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

    print("========== DEBUG PRESUPUESTO API: Iniciando ==========")
    print(f"DEBUG API: Data recibida completa: {data}")
    print(f"DEBUG API: Tipo de data: {type(data)}")
    
    # Validar campos requeridos
    campos_requeridos = ['id_empleado', 'id_sucursal', 'fecha_presupuesto', 'detalle_presupuesto', 'id_proveedor', 'id_pedido_compra', 'fecha_vencimiento', 'estado']
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None:
            print(f"❌ DEBUG API: Falta campo requerido: {campo}")
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
        fecha_vencimiento = data['fecha_vencimiento']
        estado = data['estado']
        
        print(f"DEBUG API: detalle_presupuesto raw: {detalle_presupuesto}")
        print(f"DEBUG API: Tipo de detalle_presupuesto: {type(detalle_presupuesto)}")
        print(f"DEBUG API: Cantidad de items en detalle: {len(detalle_presupuesto) if isinstance(detalle_presupuesto, list) else 'NO ES LISTA'}")

        # Verificar que el estado es válido
        if estado not in ESTADOS_PRESUPUESTO:
            return jsonify({
                'success': False,
                'error': f'El estado {estado} no es válido.'
            }), 400

        # Crear detalle del presupuesto
        print("DEBUG API: Creando DTOs de detalle...")
        detalle_dto = []
        
        for idx, item in enumerate(detalle_presupuesto):
            print(f"DEBUG API: Procesando item {idx + 1}: {item}")
            
            dto = PresupuestoProvDetalleDto(
                id_producto=item['id_producto'],
                cantidad=item['cantidad'],
                precio_unitario=item.get('precio_unitario', 0)
            )
            
            print(f"  - DTO creado: id_producto={dto.id_producto}, cantidad={dto.cantidad}, precio={dto.precio_unitario}")
            detalle_dto.append(dto)
        
        print(f"DEBUG API: Total DTOs creados: {len(detalle_dto)}")

        # Crear cabecera del presupuesto
        print("DEBUG API: Creando DTO de cabecera...")
        cabecera_dto = PresupuestoProvDto(
            id_presupuesto=None,
            id_empleado=id_empleado,
            id_sucursal=id_sucursal,
            id_proveedor=id_proveedor,
            id_pedido_compra=id_pedido_compra,
            estado=EstadoPresupuestoProveedor(id=ESTADOS_PRESUPUESTO[estado], descripcion=None),
            fecha_presupuesto=date.fromisoformat(fecha_presupuesto),
            fecha_vencimiento=date.fromisoformat(fecha_vencimiento),
            detalle_presupuesto=detalle_dto
        )
        
        print(f"DEBUG API: Cabecera DTO creada con {len(cabecera_dto.detalle_presupuesto)} detalles")
        print(f"DEBUG API: Detalle en cabecera_dto: {cabecera_dto.detalle_presupuesto}")

        # Registrar presupuesto en la base de datos
        print("DEBUG API: Llamando a agregar() del DAO...")
        resultado = ppdao.agregar(presupuesto_dto=cabecera_dto)
        
        if resultado:
            print("DEBUG API: Presupuesto creado exitosamente")
            return jsonify({
                'success': True,
                'error': None
            }), 201
        else:
            print("DEBUG API: Error al crear presupuesto (DAO retornó False)")
            return jsonify({
                'success': False,
                'error': 'No se pudo crear el presupuesto. Consulte con el administrador.'
            }), 500

    except Exception as e:
        print(f"❌ ERROR en add_presupuesto API: {str(e)}")
        import traceback
        traceback.print_exc()
        
        app.logger.error(f"Error al crear presupuesto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500