from flask import Flask
from werkzeug.security import generate_password_hash 
## instancia para arrancar el proyecto
app = Flask (__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# Contraseña que deseas hashear
password = ""

# Generar el hash de la contraseña con un algoritmo de scrypt
hashed_password = generate_password_hash(password, method='scrypt', salt_length=16)

# Asegurarse de que el hash tenga 300 caracteres
print(hashed_password[:300])

# ============================================================
# IMPORTAR REFERENCIALES
# ============================================================
from app.rutas.referenciales.ciudad.ciudad_routes import ciumod
from app.rutas.referenciales.pais.pais_routes import paismod
from app.rutas.referenciales.nacionalidad.nacionalidad_routes import nacmod
from app.rutas.referenciales.producto.producto_routes import promod
from app.rutas.referenciales.persona.persona_routes import permod
from app.rutas.referenciales.proveedor.proveedor_routes import provmod
from app.rutas.referenciales.cliente.cliente_routes import climod
from app.rutas.referenciales.sucursal.sucursal_routes import sucmod
from app.rutas.referenciales.deposito.deposito_routes import depomod
from app.rutas.referenciales.cargo.cargo_routes import carmod
from app.rutas.referenciales.estado_civil.estado_civil_routes import estmod
from app.rutas.referenciales.sexo.sexo_routes import sexomod
from app.rutas.referenciales.marca.marca_routes import marcmod
from app.rutas.referenciales.emisora.emisora_routes import emismod
from app.rutas.referenciales.tipo_producto.tipo_producto_routes import tipprodmod

from app.rutas.login.login_routes import login_bp

app.register_blueprint(login_bp)

# ============================================================
# IMPORTAR GESTIONAR COMPRAS (ROUTES)
# ============================================================
from app.rutas.gestionar_compras.registrar_pedido_compras.registrar_pedidos_compras_routes \
    import pdcmod

from app.rutas.gestionar_compras.registrar_presupuesto_proveedor.registrar_presupuesto_proveedor_routes \
    import pdpmod

from app.rutas.gestionar_compras.generar_orden_compra.generar_orden_compra_routes \
    import ocmod

from app.rutas.gestionar_compras.gestionar_la_compra.gestionar_la_compra_routes import compramod

from app.rutas.gestionar_compras.registrar_ajustes.registrar_ajustes_routes import ajustemod

from app.rutas.gestionar_compras.registrar_nota_compra.registrar_nota_compra_routes import notasmod


# ============================================================
# IMPORTAR GESTIONAR SERVICIOS (ROUTES)
# ============================================================
from app.rutas.gestionar_servicios.registrar_solicitud_servicio.registrar_solicitud_servicio_routes import solicitudmod
from app.rutas.gestionar_servicios.registrar_presupuesto_servicio.registrar_presupuesto_servicio_routes import presupuestomod
from app.rutas.gestionar_servicios.generar_orden_servicio.generar_orden_servicio_routes import ordenmod
from app.rutas.gestionar_servicios.registrar_promociones.registrar_promociones_routes import promocionmod
from app.rutas.gestionar_servicios.registrar_descuentos.registrar_descuentos_routes import descuentomod

# ============================================================
# REGISTRAR REFERENCIALES 
# ============================================================
modulo0 = '/referenciales'
app.register_blueprint(ciumod, url_prefix=f'{modulo0}/ciudad')
app.register_blueprint(paismod, url_prefix=f'{modulo0}/pais')
app.register_blueprint(nacmod, url_prefix=f'{modulo0}/nacionalidad')
app.register_blueprint(promod, url_prefix=f'{modulo0}/producto')
app.register_blueprint(permod, url_prefix=f'{modulo0}/persona')
app.register_blueprint(provmod, url_prefix=f'{modulo0}/proveedor')
app.register_blueprint(climod, url_prefix=f'{modulo0}/cliente')
app.register_blueprint(sucmod, url_prefix=f'{modulo0}/sucursal')
app.register_blueprint(depomod, url_prefix=f'{modulo0}/deposito')
app.register_blueprint(carmod, url_prefix=f'{modulo0}/cargo')
app.register_blueprint(estmod, url_prefix=f'{modulo0}/estado_civil')
app.register_blueprint(sexomod, url_prefix=f'{modulo0}/sexo')
app.register_blueprint(marcmod, url_prefix=f'{modulo0}/marca')
app.register_blueprint(emismod, url_prefix=f'{modulo0}/emisora')
app.register_blueprint(tipprodmod, url_prefix=f'{modulo0}/tipo_producto')


# ============================================================
# REGISTRAR MÓDULOS - GESTIONAR COMPRAS (ROUTES)
# ============================================================
modulo1 = '/gestionar-compras'
app.register_blueprint(pdcmod, url_prefix=f'{modulo1}/registrar-pedido-compras')
app.register_blueprint(pdpmod, url_prefix=f'{modulo1}/registrar-presupuesto-proveedor')
app.register_blueprint(ocmod, url_prefix=f'{modulo1}/generar-orden-compra')
app.register_blueprint(compramod, url_prefix=f'{modulo1}/gestionar-compra')
app.register_blueprint(ajustemod, url_prefix=f'{modulo1}/registrar-ajustes')
app.register_blueprint(notasmod, url_prefix=f'{modulo1}/registrar-notas')


# ============================================================
# REGISTRAR MÓDULOS - GESTIONAR SERVICIOS (ROUTES)
# ============================================================
modulo2 = '/gestionar-servicios'
app.register_blueprint(solicitudmod, url_prefix=f'{modulo2}/solicitud-servicio')
app.register_blueprint(presupuestomod, url_prefix=f'{modulo2}/presupuesto-servicio')
app.register_blueprint(ordenmod, url_prefix=f'{modulo2}/orden-servicio')
app.register_blueprint(promocionmod, url_prefix=f'{modulo2}/promocion')
app.register_blueprint(descuentomod, url_prefix=f'{modulo2}/descuento')




# ============================================================
# IMPORTAR APIS v1 - REFERENCIALES
# ============================================================
from app.rutas.referenciales.ciudad.ciudad_api import ciuapi
from app.rutas.referenciales.pais.pais_api import paiapi
from app.rutas.referenciales.nacionalidad.nacionalidad_api import nacapi
from app.rutas.referenciales.producto.producto_api import proapi
from app.rutas.referenciales.persona.persona_api import perapi
from app.rutas.referenciales.proveedor.proveedor_api import provapi
from app.rutas.referenciales.cliente.cliente_api import cliapi
from app.rutas.referenciales.sucursal.sucursal_api import sucapi
from app.rutas.referenciales.deposito.deposito_api import depoapi
from app.rutas.referenciales.cargo.cargo_api import carapi
from app.rutas.referenciales.estado_civil.estado_civil_api import estadocivilapi
from app.rutas.referenciales.sexo.sexo_api import sexoapi
from app.rutas.referenciales.marca.marca_api import marcaapi
from app.rutas.referenciales.emisora.emisora_api import emisoraapi
from app.rutas.referenciales.tipo_producto.tipo_producto_api import tipo_producto_api

# ============================================================
# IMPORTAR APIS v1 - GESTIONAR COMPRAS
# ============================================================
from app.rutas.gestionar_compras.registrar_pedido_compras.registrar_pedido_compras_api \
    import pdcapi

from app.rutas.gestionar_compras.registrar_presupuesto_proveedor.registrar_presupuesto_proveedor_api \
    import pdpapi

from app.rutas.gestionar_compras.generar_orden_compra.generar_orden_compra_api \
    import ocapi

from app.rutas.gestionar_compras.gestionar_la_compra.gestionar_la_compra_api import compraapi

from app.rutas.gestionar_compras.registrar_ajustes.registrar_ajustes_api import ajusteapi

from app.rutas.gestionar_compras.registrar_nota_compra.registrar_nota_compra_api import notasapi


# ============================================================
# IMPORTAR APIS v1 - GESTIONAR SERVICIOS
# ============================================================
from app.rutas.gestionar_servicios.registrar_solicitud_servicio.registrar_solicitud_servicio_api import solicitudapi

from app.rutas.gestionar_servicios.registrar_presupuesto_servicio.registrar_presupuesto_servicio_api import presupuestoapi

from app.rutas.gestionar_servicios.generar_orden_servicio.generar_orden_servicio_api import ordenapi

from app.rutas.gestionar_servicios.registrar_promociones.registrar_promociones_api import promocionapi

from app.rutas.gestionar_servicios.registrar_descuentos.registrar_descuentos_api import descuentoapi



# ============================================================
# REGISTRAR APIS v1 - REFERENCIALES
# ============================================================
version1 = '/api/v1'
app.register_blueprint(ciuapi, url_prefix=version1)
app.register_blueprint(paiapi, url_prefix=version1)
app.register_blueprint(nacapi, url_prefix=version1)
app.register_blueprint(proapi, url_prefix=version1)
app.register_blueprint(perapi, url_prefix=version1)
app.register_blueprint(provapi, url_prefix=version1)
app.register_blueprint(cliapi, url_prefix=version1)
app.register_blueprint(sucapi, url_prefix=version1)
app.register_blueprint(depoapi, url_prefix=version1)
app.register_blueprint(carapi, url_prefix=version1)
app.register_blueprint(estadocivilapi, url_prefix=version1)
app.register_blueprint(sexoapi, url_prefix=version1)
app.register_blueprint(marcaapi, url_prefix=version1)
app.register_blueprint(emisoraapi, url_prefix=version1)
app.register_blueprint(tipo_producto_api, url_prefix=version1)


# ============================================================
# REGISTRAR APIS v1 - GESTIONAR COMPRAS
# ============================================================
app.register_blueprint(pdcapi, url_prefix=f'{version1}/{modulo1}/registrar-pedido-compras')
app.register_blueprint(pdpapi, url_prefix=f'{version1}/{modulo1}/registrar-presupuesto-proveedor')
app.register_blueprint(ocapi, url_prefix=f'{version1}{modulo1}/generar-orden-compra')
app.register_blueprint(compraapi, url_prefix=f'{version1}{modulo1}/gestionar-compra')
app.register_blueprint(ajusteapi, url_prefix=f'{version1}{modulo1}/registrar-ajustes')
app.register_blueprint(notasapi, url_prefix=f'{version1}{modulo1}/registrar-notas')


# ============================================================
# REGISTRAR APIS v1 - GESTIONAR SERVICIOS
# ============================================================
app.register_blueprint(solicitudapi, url_prefix=f'{version1}{modulo2}/solicitud-servicio')
app.register_blueprint(presupuestoapi, url_prefix=f'{version1}{modulo2}/presupuesto-servicio')
app.register_blueprint(ordenapi, url_prefix=f'{version1}{modulo2}/orden-servicio')
app.register_blueprint(promocionapi, url_prefix=f'{version1}{modulo2}/promocion')
app.register_blueprint(descuentoapi, url_prefix=f'{version1}{modulo2}/descuento')





print("\n========== RUTAS REGISTRADAS ==========")
for rule in app.url_map.iter_rules():
    if 'generar-orden-compra' in rule.rule or 'detalle-presupuesto' in rule.rule:
        print(f"{rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
print("========================================\n")