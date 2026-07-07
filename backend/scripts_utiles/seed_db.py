import os
import sys
import django
import random
import socket
import datetime
from django.utils.crypto import get_random_string
from django.core.management import call_command
from django.db import connection
from django.utils import timezone
from datetime import timedelta

# 1. Configuración de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context, schema_exists
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito import Carrito
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito_item import CarritoItem
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.models.tipo_pago import TipoPago
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.detalle_factura import DetalleFactura
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.factura import Factura
from apps.gestionDeVentasYFacturacion.cu24_gestionar_logistica.models.delivery_zone import DeliveryZone
from apps.gestionDeClientes.cu25_gestionar_solicitud_de_restock.models.restock_request import RestockRequest
from apps.gestionDeClientes.cu26_gestionar_resenas.models.resena import Resena
from apps.customers.models import Client, Domain, Usuario, Rol, Plan, Cliente, Permiso

def obtener_ip_dominio():
    base_domain = os.environ.get('REACT_APP_DOMAIN_MAIN')
    if not base_domain or base_domain == 'localhost' or '192.168' in base_domain:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return f"{ip}.nip.io"
        except Exception:
            return "localhost"
    return base_domain

def sync_tenant_schema(tenant):
    if not schema_exists(tenant.schema_name):
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE SCHEMA {connection.ops.quote_name(tenant.schema_name)}')
        connection.set_schema_to_public()
    try:
        call_command(
            'migrate_schemas',
            tenant=True,
            schema_name=tenant.schema_name,
            run_syncdb=True,
            interactive=False,
            verbosity=0,
        )
    except Exception as e:
        print(f"     [!] Aviso al migrar {tenant.schema_name}: {e}")
    finally:
        connection.set_schema_to_public()

def get_or_create_tenant(schema_name, defaults):
    tenant = Client.objects.filter(schema_name=schema_name).first()
    created = tenant is None
    if created:
        tenant = Client(schema_name=schema_name, **defaults)
        tenant.auto_create_schema = False
        tenant.save()
    else:
        for field, value in defaults.items():
            setattr(tenant, field, value)
        tenant.auto_create_schema = False
        tenant.save()

    sync_tenant_schema(tenant)
    return tenant, created

def ensure_tenant_admin(tenant, rol_admin):
    user, created = Usuario.objects.get_or_create(
        email=f"admin@{tenant.schema_name}.com",
        defaults={'tenant': tenant, 'is_staff': True},
    )
    if created:
        user.set_password('Pass123@')
    user.tenant = tenant
    user.is_staff = True
    user.save()
    user.roles.add(rol_admin)
    return user

def generar_datos_prueba():
    nombres = ["Juan", "Maria", "Pedro", "Ana", "Luis", "Carlos", "Laura", "Sofia", "Diego", "Lucia", "Jorge", "Marta", "Elena", "Miguel", "Paula", "Andres", "Camila", "Fernanda", "Gabriel", "Hugo", "Isabella", "Jose", "Karen", "Lucas", "Manuel", "Natalia", "Oscar", "Patricia", "Roberto", "Sara"]
    apellidos = ["Garcia", "Perez", "Rodriguez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Gomez", "Martin", "Jimenez", "Ruiz", "Hernandez", "Diaz", "Moreno", "Alvarez", "Romero", "Alonso", "Gutierrez", "Navarro", "Torres", "Dominguez", "Vazquez", "Ramos", "Gil", "Ramirez", "Serrano", "Blanco", "Molina", "Morales", "Suarez"]
    return nombres, apellidos

def ejecutar():
    print("--- Iniciando Sincronización Maestra (Seeder Principal) ---")
    base_domain = obtener_ip_dominio()
    print(f"Dominio Base detectado: {base_domain}")

    with schema_context('public'):
        # 1. PERMISOS DEL SISTEMA Y REPORTES
        print("\n1. Configurando Permisos...")
        permisos_data = [
            ("Acceso Total Sistema", "SYS_ALL", "Sistema", True, "Acceso irrestricto a todo el SaaS"),
            ("Gestionar Tenants", "SYS_TENANTS", "Sistema", True, "Crear y eliminar tiendas"),
            ("Gestionar Productos", "STORE_PRODUCTS", "Inventario", True, "Crear, editar y eliminar productos"),
            ("Gestionar Ventas", "STORE_SALES", "Ventas", True, "Ver y procesar facturas"),
            ("Ver Reportes", "STORE_REPORTS", "Análisis", True, "Ver métricas de la tienda"),
            ("Realizar Compras", "CLIENT_BUY", "Tienda", True, "Añadir al carrito y pagar"),
            ("Ver Historial", "CLIENT_HISTORY", "Tienda", True, "Ver sus pedidos anteriores"),
            ("Reportes Estáticos", "REP_ESTATICO", "Reportes", False, "Permite generar y descargar reportes predefinidos"),
            ("Reportes Dinámicos", "REP_DINAMICO", "Reportes", False, "Permite armar reportes personalizados con métricas"),
            ("Reportes con IA (Voz)", "REP_AUDIO", "Reportes", False, "Permite realizar consultas mediante voz"),
            ("Dashboard Avanzado", "VER_DASHBOARD_AVANZADO", "Reportes", False, "Métricas avanzadas y predicciones"),
            ("Exportar Clientes", "EXPORTAR_CLIENTES", "Clientes", False, "Permite descargar padrón de clientes"),
            ("Configurar Pagos", "CONFIGURACION_PAGOS", "Configuración", False, "Vincular pasarelas de pago"),
        ]

        permisos_obj = {}
        for nombre, codigo, modulo, es_basico, desc in permisos_data:
            p, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'modulo': modulo, 'es_basico': es_basico, 'descripcion': desc, 'activo': True}
            )
            permisos_obj[codigo] = p

        # 2. ROLES
        print("2. Configurando Roles...")
        roles_data = [
            ("Administrador", 1, ["SYS_ALL", "SYS_TENANTS", "STORE_PRODUCTS", "STORE_SALES", "STORE_REPORTS"]),
            ("Vendedor", 2, ["STORE_PRODUCTS", "STORE_SALES", "STORE_REPORTS"]),
            ("Cliente", 3, ["CLIENT_BUY", "CLIENT_HISTORY"]),
        ]

        for nombre_rol, nivel, codigos in roles_data:
            rol, _ = Rol.objects.get_or_create(
                nombre=nombre_rol,
                defaults={'nivel': nivel, 'descripcion': f"Rol {nombre_rol}", 'activo': True}
            )
            rol.permisos.set([permisos_obj[c] for c in codigos if c in permisos_obj])
        rol_admin = Rol.objects.get(nombre='Administrador', tenant=None)

        # 3. PLANES SAAS
        print("3. Configurando Planes de Suscripción...")
        planes_config = [
            {"nombre": "Gratis", "precio_mensual": 0.0, "precio_anual": 0.0, "max_usuarios": 2, "max_productos": 50, "facturacion_max": 1000.0, "permisos": []},
            {"nombre": "Standard", "precio_mensual": 29.0, "precio_anual": 290.0, "max_usuarios": 5, "max_productos": 500, "facturacion_max": 10000.0, "permisos": ["REP_ESTATICO"]},
            {"nombre": "Gold", "precio_mensual": 69.0, "precio_anual": 690.0, "max_usuarios": 15, "max_productos": 5000, "facturacion_max": 500000.0, "permisos": ["REP_ESTATICO", "VER_DASHBOARD_AVANZADO", "EXPORTAR_CLIENTES", "CONFIGURACION_PAGOS"]},
            {"nombre": "Profesional", "precio_mensual": 99.0, "precio_anual": 990.0, "max_usuarios": 999999, "max_productos": 999999, "facturacion_max": None, "permisos": ["REP_ESTATICO", "VER_DASHBOARD_AVANZADO", "EXPORTAR_CLIENTES", "CONFIGURACION_PAGOS", "REP_DINAMICO", "REP_AUDIO"]}
        ]

        planes_obj = {}
        for p_data in planes_config:
            plan, _ = Plan.objects.get_or_create(
                nombre=p_data['nombre'],
                defaults={
                    'precio_mensual': p_data['precio_mensual'],
                    'precio_anual': p_data['precio_anual'],
                    'max_usuarios': p_data['max_usuarios'],
                    'max_productos': p_data['max_productos'],
                    'facturacion_max': p_data.get('facturacion_max', None),
                }
            )
            Plan.objects.filter(id=plan.id).update(
                precio_mensual=p_data['precio_mensual'],
                max_usuarios=p_data['max_usuarios'],
                max_productos=p_data['max_productos'],
                facturacion_max=p_data.get('facturacion_max', None)
            )
            plan.permisos.set([permisos_obj[c] for c in p_data['permisos'] if c in permisos_obj])
            planes_obj[plan.nombre] = plan

        # 4. TIENDAS (TENANTS)
        print("\n4. Configurando Múltiples Tiendas de Ejemplo (Super Población)...")
        config_tiendas = [
            {'schema': 'tecno', 'nombre': 'Tecno Smart', 'cat': 'Electrónica', 'plan': planes_obj['Gratis']},
            {'schema': 'moda', 'nombre': 'Moda Express', 'cat': 'Ropa', 'plan': planes_obj['Standard']},
            {'schema': 'hogar', 'nombre': 'Hogar & Deco', 'cat': 'Hogar', 'plan': planes_obj['Profesional']},
            {'schema': 'deportes', 'nombre': 'Sports Life', 'cat': 'Deportes', 'plan': planes_obj['Standard']},
            {'schema': 'salud', 'nombre': 'Salud 360', 'cat': 'Salud y Belleza', 'plan': planes_obj['Profesional']},
            {'schema': 'mascotas', 'nombre': 'Pet Shop', 'cat': 'Mascotas', 'plan': planes_obj['Gratis']},
            {'schema': 'libros', 'nombre': 'Ateneo Literario', 'cat': 'Librería', 'plan': planes_obj['Profesional']},
            {'schema': 'juguetes', 'nombre': 'Kids World', 'cat': 'Juguetes', 'plan': planes_obj['Standard']},
            {'schema': 'ferreteria', 'nombre': 'Ferretería Central', 'cat': 'Ferretería', 'plan': planes_obj['Gold']},
            {'schema': 'autos', 'nombre': 'Motor Parts', 'cat': 'Autopartes', 'plan': planes_obj['Profesional']},
        ]

        datos_productos = {
            'Electrónica': [("Laptop Pro 14", 8500), ("Smartphone Z", 4200), ("Audífonos BT", 800), ("Monitor 27", 2500), ("Teclado Mecánico", 600), ("Mouse Inalámbrico", 300), ("Tablet 10", 3200), ("Smartwatch", 1500), ("Cámara Web", 450), ("Altavoz Inteligente", 1200)],
            'Ropa': [("Chaqueta Jean", 350), ("Tenis Runner", 550), ("Gorra Classic", 120), ("Camiseta Básica", 80), ("Pantalón Chino", 200), ("Sudadera con Capucha", 280), ("Zapatos de Vestir", 650), ("Bufanda Invierno", 90), ("Calcetines Pack", 50), ("Cinturón Cuero", 150)],
            'Hogar': [("Silla Ergonómica", 1200), ("Lámpara Minimal", 250), ("Mesa de Centro", 800), ("Sofá 3 Cuerpos", 4500), ("Estantería", 600), ("Cuadro Abstracto", 350), ("Alfombra Sala", 400), ("Set de Cubiertos", 180), ("Sartén Antiadherente", 220), ("Cafetera", 380)],
            'Deportes': [("Balón de Fútbol", 150), ("Raqueta Tenis", 450), ("Pesas 5kg", 200), ("Bicicleta Montaña", 3500), ("Botella Agua", 50), ("Esterilla Yoga", 120), ("Zapatillas Trail", 700), ("Guantes Gimnasio", 80), ("Cuerda Saltar", 60), ("Bolsa Deporte", 250)],
            'Salud y Belleza': [("Crema Hidratante", 150), ("Perfume Floral", 450), ("Set Maquillaje", 300), ("Secador de Pelo", 250), ("Máquina Afeitar", 180), ("Vitaminas", 120), ("Protector Solar", 100), ("Cepillo Eléctrico", 350), ("Plancha de Pelo", 400), ("Mascarilla Facial", 40)],
            'Mascotas': [("Alimento Perro 15kg", 400), ("Juguete Gato", 50), ("Cama Mascota", 250), ("Correa Extensible", 120), ("Rascador Gato", 350), ("Champú Perro", 80), ("Collar Antipulgas", 150), ("Comedero Automático", 450), ("Transportín", 300), ("Snacks Premium", 60)],
            'Librería': [("Novela Bestseller", 120), ("Libro Programación", 250), ("Agenda 2024", 80), ("Set Bolígrafos", 50), ("Cuaderno Notas", 40), ("Mochila Escolar", 350), ("Libro Infantil", 90), ("Marcadores Colores", 110), ("Calculadora Científica", 180), ("Diccionario Inglés", 150)],
            'Juguetes': [("Lego Set", 600), ("Muñeca Articulada", 150), ("Coche Radiocontrol", 350), ("Juego de Mesa", 250), ("Rompecabezas 1000", 120), ("Oso Peluche", 180), ("Pistola Agua", 80), ("Set Herramientas Niño", 200), ("Plastilina Pack", 60), ("Triciclo", 450)],
            'Ferretería': [("Taladro Percutor", 550), ("Set Destornilladores", 120), ("Caja Herramientas", 300), ("Sierra Circular", 800), ("Martillo", 80), ("Cinta Métrica", 40), ("Alicates", 60), ("Llave Inglesa", 90), ("Tornillos Pack", 30), ("Pegamento Industrial", 50)],
            'Autopartes': [("Aceite Motor 5L", 250), ("Batería 12V", 850), ("Juego Pastillas Freno", 350), ("Filtro de Aire", 80), ("Bujías x4", 120), ("Lámpara Halógena", 50), ("Neumático R15", 950), ("Amortiguador", 600), ("Correa Distribución", 450), ("Líquido Refrigerante", 90)]
        }

        for conf in config_tiendas:
            tenant, created = get_or_create_tenant(
                conf['schema'],
                {
                    'name': conf['nombre'],
                    'plan': conf['plan'],
                    'nombre_comercial': conf['nombre'],
                    'categoria_tienda': conf['cat']
                },
            )
            tenant.plan = conf['plan']
            tenant.save()

            domain_url = f"{conf['schema']}.{base_domain}" if base_domain != 'localhost' else f"{conf['schema']}.localhost"
            Domain.objects.get_or_create(domain=domain_url, tenant=tenant, defaults={'is_primary': True})
            ensure_tenant_admin(tenant, rol_admin)

            # Configuración de Logística y Envíos (CU-24): ciudad, WhatsApp y flags de entrega.
            ciudad = random.choice(['La Paz', 'Santa Cruz', 'Cochabamba', 'El Alto', 'Sucre'])
            tenant.ciudad = ciudad
            tenant.whatsapp = '72684507'
            tenant.enable_local_delivery = True
            tenant.enable_national_shipping = True
            tenant.save()

            print(f"   -> Tienda {conf['nombre']} ({conf['schema']}) en Plan {conf['plan'].nombre} | Ciudad {ciudad}")

    # 5. POBLAR CADA TIENDA CON MASIVOS DATOS (Super Población)
    nombres_base, apellidos_base = generar_datos_prueba()
    
    for conf in config_tiendas:
        print(f"\n   --- Poblando masivamente tenant: {conf['nombre']} ---")
        with schema_context(conf['schema']):
            # Limpieza para evitar duplicados en pruebas repetidas (con manejo de excepciones por migraciones desincronizadas)
            try:
                Resena.objects.all().delete()           # CU-27 (antes de Cliente/Producto por FK)
                RestockRequest.objects.all().delete()   # CU-25 (antes de Cliente/Producto por FK)
                DeliveryZone.objects.all().delete()      # CU-24
                DetalleFactura.objects.all().delete()
                Factura.objects.all().delete()
                Pedido.objects.all().delete()
                CarritoItem.objects.all().delete()
                Carrito.objects.all().delete()
                Producto.objects.all().delete()
                Categoria.objects.all().delete()
                Cliente.objects.all().delete()
                TipoPago.objects.all().delete()
            except Exception as e:
                print("     [!] Aviso al limpiar datos: No se pudieron borrar algunos registros antiguos. Se agregarán nuevos datos sin borrar los anteriores.")

            cat_obj, _ = Categoria.objects.get_or_create(nombre=conf['cat'])

            # Crear Productos
            prods_creados = []
            for nom, precio in datos_productos.get(conf['cat'], []):
                img = f"https://ui-avatars.com/api/?name={nom.replace(' ', '+')}&background=random&size=500"
                p = Producto.objects.create(
                    nombre=nom, precio=precio, stock=random.randint(50, 500),
                    categoria=cat_obj, imagen_url=img,
                    sku=f"SKU-{get_random_string(5).upper()}", activo=True
                )
                prods_creados.append(p)

            # --- CU-24 Logística: Zonas de Delivery de la tienda ---
            for zname, zprice in [('Centro', 10), ('Zona Sur', 15), ('Zona Norte', 20), ('Encomienda Nacional', 35)]:
                DeliveryZone.objects.get_or_create(zone_name=zname, defaults={'price': zprice, 'activo': True})

            # --- CU-24 Preventa (Reservas): marcar los primeros productos como preorder ---
            for prod in prods_creados[:2]:
                prod.is_preorder = True
                prod.estimated_arrival_date = (timezone.now() + timedelta(days=random.randint(10, 30))).date()
                prod.preorder_discount_percentage = random.choice([5, 10, 15])
                prod.save()

            # --- CU-25 Restock: dejar los últimos productos agotados (stock 0) para probar la intención de compra ---
            productos_agotados = prods_creados[-2:] if len(prods_creados) >= 2 else []
            for prod in productos_agotados:
                prod.stock = 0
                prod.save()

            tipo_pago_efec, _ = TipoPago.objects.get_or_create(nombre='EFECTIVO', defaults={'estado': 'ACTIVO'})
            tipo_pago_tarj, _ = TipoPago.objects.get_or_create(nombre='TARJETA', defaults={'estado': 'ACTIVO'})
            tipo_pago_trans, _ = TipoPago.objects.get_or_create(nombre='TRANSFERENCIA', defaults={'estado': 'ACTIVO'})
            tipos_pago = [tipo_pago_efec, tipo_pago_tarj, tipo_pago_trans]

            # Crear Clientes Masivos (50 clientes por tenant)
            clientes_creados = []
            for _ in range(50):
                nombre_random = random.choice(nombres_base)
                apellido_random = random.choice(apellidos_base)
                email_random = f"{nombre_random.lower()}.{apellido_random.lower()}.{get_random_string(4).lower()}@gmail.com"
                
                cliente = Cliente.objects.create(
                    nombre=f"{nombre_random} {apellido_random}",
                    correo=email_random
                )
                clientes_creados.append(cliente)

            # --- CU-25 Intención de Compra: solicitudes de restock sobre los productos agotados ---
            for prod in productos_agotados:
                for cliente in random.sample(clientes_creados, min(5, len(clientes_creados))):
                    RestockRequest.objects.get_or_create(cliente=cliente, producto=prod)

            # Crear Pedidos Históricos Masivos (alrededor de 300-500 facturas por tenant)
            num_pedidos_totales = random.randint(300, 500)
            
            # Para optimizar inserciones en Django
            from django.db import transaction
            
            with transaction.atomic():
                for _ in range(num_pedidos_totales):
                    cliente = random.choice(clientes_creados)
                    dias_atras = random.randint(1, 365)
                    fake_date = timezone.now() - timedelta(days=dias_atras)
                    
                    carrito = Carrito.objects.create(cliente=cliente, estado='CERRADO')
                    Carrito.objects.filter(id=carrito.id).update(fecha_creacion=fake_date)
                    
                    # Cantidad de items por carrito (1 a 4)
                    cant_items = random.randint(1, 4)
                    productos_seleccionados = random.sample(prods_creados, cant_items) if len(prods_creados) >= cant_items else prods_creados
                    
                    subtotal_carrito = 0
                    items_a_crear = []
                    for prod in productos_seleccionados:
                        cant = random.randint(1, 3)
                        subtotal = cant * prod.precio
                        subtotal_carrito += subtotal
                        
                        items_a_crear.append(CarritoItem(
                            carrito=carrito, 
                            producto=prod, 
                            cantidad=cant
                        ))
                    
                    # Guardar items
                    for it in items_a_crear:
                        it.save() 
                    
                    pedido = Pedido.objects.create(
                        carrito=carrito,
                        estado=random.choices(['ENTREGADO', 'EN_CAMINO', 'PENDIENTE', 'CANCELADO'], weights=[80, 10, 5, 5])[0]
                    )
                    Pedido.objects.filter(id=pedido.id).update(fecha_creacion=fake_date)
                    
                    if pedido.estado != 'CANCELADO':
                        nro_fact = f"FAC-{conf['schema'][:3].upper()}-{get_random_string(8).upper()}"
                        factura = Factura.objects.create(
                            nro=nro_fact,
                            pedido=pedido,
                            cliente=cliente,
                            tipo_pago=random.choice(tipos_pago),
                            monto_total=subtotal_carrito,
                            estado='VIGENTE'
                        )
                        Factura.objects.filter(nro=nro_fact).update(fecha=fake_date.date(), hora=fake_date.time())
                        
                        detalles_a_crear = []
                        for it in items_a_crear:
                            detalles_a_crear.append(DetalleFactura(
                                factura=factura,
                                producto=it.producto,
                                cantidad=it.cantidad,
                                precio_unitario=it.producto.precio,
                                total=it.cantidad * it.producto.precio
                            ))
                        DetalleFactura.objects.bulk_create(detalles_a_crear)

            # --- CU-24 Preventa: RESERVAS (pedidos PENDIENTE de productos en preventa, con envío) ---
            zonas_disp = list(DeliveryZone.objects.all())
            reservas_creadas = 0
            for prod_pre in prods_creados[:2]:  # los 2 productos marcados como preventa
                for cli in random.sample(clientes_creados, min(3, len(clientes_creados))):
                    carrito_r = Carrito.objects.create(cliente=cli, estado='CERRADO')
                    CarritoItem.objects.create(carrito=carrito_r, producto=prod_pre, cantidad=1)
                    z = random.choice(zonas_disp) if zonas_disp else None
                    Pedido.objects.create(
                        carrito=carrito_r,
                        estado='PENDIENTE',
                        tipo_envio='DELIVERY_LOCAL' if z else None,
                        costo_envio=(z.price if z else 0),
                        zona_envio=(z.zone_name if z else None),
                        observaciones='Reserva de preventa',
                    )
                    reservas_creadas += 1

            # --- CU-27 Reseñas: compradores con pedidos ENTREGADOS reseñan lo que compraron ---
            comentarios = ['Excelente calidad!', 'Llegó rápido y en buen estado.', 'Muy bueno, recomendado.',
                           'Cumple lo prometido.', 'Buen precio y calidad.', 'Volvería a comprar sin dudarlo.']
            resenas_creadas = 0
            vistos = set()
            pedidos_entregados = (Pedido.objects
                                  .filter(estado='ENTREGADO')
                                  .select_related('carrito__cliente')
                                  .prefetch_related('carrito__items__producto'))
            for ped in pedidos_entregados:
                if resenas_creadas >= 80:
                    break
                cli = ped.carrito.cliente
                for it in ped.carrito.items.all():
                    clave = (cli.id, it.producto_id)
                    if clave in vistos:
                        continue
                    vistos.add(clave)
                    Resena.objects.get_or_create(
                        cliente=cli, producto=it.producto,
                        defaults={'calificacion': random.randint(3, 5), 'comentario': random.choice(comentarios)},
                    )
                    resenas_creadas += 1
                    if resenas_creadas >= 80:
                        break

            print(f"   [OK] {len(prods_creados)} Productos ({len(productos_agotados)} agotados, 2 en preventa), "
                  f"{len(clientes_creados)} Clientes, {num_pedidos_totales} Pedidos, 4 Zonas, "
                  f"{reservas_creadas} Reservas, {resenas_creadas} Reseñas.")

    print("\nSEEDER MAESTRO EJECUTADO CON ÉXITO.")
    print("   El sistema está SUPER POBLADO y listo con múltiples tenants, planes, reportes y muchísimos datos de prueba.")

if __name__ == "__main__":
    ejecutar()
