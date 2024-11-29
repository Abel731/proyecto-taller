from datetime import date
from flask import Blueprint, jsonify, request, current_app as app
from app.dao.gestionar_compras.registrar_presupuesto_proveedor.presupuesto_de_proveedor_dao \
    import PresupuestoProvDao
from app.dao.gestionar_compras.registrar_pedido_compras.pedido_de_compras_dao \
    import PedidoDeComprasDao

pdpapi = Blueprint('pdpapi', __name__)

