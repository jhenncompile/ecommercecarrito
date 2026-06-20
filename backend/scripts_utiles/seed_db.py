import os
import sys
import django
import random
import socket
from django.utils.crypto import get_random_string

# 1. Configuración de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from apps.negocio.models import Categoria, Producto, Pedido, Factura, DetalleFactura, TipoPago
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito import Carrito
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito_item import CarritoItem
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

def ejecutar():
    print("--- Iniciando Sincronización Maestra (Seeder Principal) ---")
    base_domain = obtener_ip_dominio()
    print(f"Dominio Base detectado: {base_domain}")

    with schema_context('public'):
        # ---------------------------------------------------------
        # 1. PERMISOS DEL SISTEMA Y REPORTES
        # ---------------------------------------------------------
        print("\n1. Configurando Permisos...")
        permisos_data = [
            # Super Usuario
            ("Acceso Total Sistema", "SYS_ALL", "Sistema", True, "Acceso irrestricto a todo el SaaS"),
            ("Gestionar Tenants", "SYS_TENANTS", "Sistema", True, "Crear y eliminar tiendas"),
            
            # Vendedor
            ("Gestionar Productos", "STORE_PRODUCTS", "Inventario", True, "Crear, editar y eliminar productos"),
            ("Gestionar Ventas", "STORE_SALES", "Ventas", True, "Ver y procesar facturas"),
            ("Ver Reportes", "STORE_REPORTS", "Análisis", True, "Ver métricas de la tienda"),
            
            # Cliente
            ("Realizar Compras", "CLIENT_BUY", "Tienda", True, "Añadir al carrito y pagar"),
            ("Ver Historial", "CLIENT_HISTORY", "Tienda", True, "Ver sus pedidos anteriores"),

            # Funcionalidades SaaS (Reportes)
            ("Reportes Estáticos", "REP_ESTATICO", "Reportes", True, "Permite generar y descargar reportes predefinidos"),
            ("Reportes Dinámicos", "REP_DINAMICO", "Reportes", False, "Permite armar reportes personalizados con métricas"),
            ("Reportes con IA (Voz)", "REP_AUDIO", "Reportes", False, "Permite realizar consultas mediante voz"),
        ]

        permisos_obj = {}
        for nombre, codigo, modulo, es_basico, desc in permisos_data:
            p, _ = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'modulo': modulo, 'es_basico': es_basico, 'descripcion': desc, 'activo': True}
            )
            permisos_obj[codigo] = p

        # ---------------------------------------------------------
        # 2. ROLES
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # 3. PLANES SAAS
        # ---------------------------------------------------------
        print("3. Configurando Planes de Suscripción...")
        planes_config = [
            {
                "nombre": "Básico", "precio_mensual": 29.0, "precio_anual": 290.0, 
                "max_usuarios": 2, "max_productos": 50,
                "permisos": ["REP_ESTATICO"]
            },
            {
                "nombre": "Medio", "precio_mensual": 59.0, "precio_anual": 590.0, 
                "max_usuarios": 5, "max_productos": 500,
                "permisos": ["REP_ESTATICO", "REP_DINAMICO"]
            },
            {
                "nombre": "Profesional", "precio_mensual": 99.0, "precio_anual": 990.0, 
                "max_usuarios": 20, "max_productos": 5000,
                "permisos": ["REP_ESTATICO", "REP_DINAMICO", "REP_AUDIO"]
            }
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
                }
            )
            plan.permisos.set([permisos_obj[c] for c in p_data['permisos'] if c in permisos_obj])
            planes_obj[plan.nombre] = plan

        # ---------------------------------------------------------
        # 4. TIENDAS (TENANTS)
        # ---------------------------------------------------------
        print("\n4. Configurando Tiendas de Ejemplo...")
        config_tiendas = [
            {'schema': 'tecno', 'nombre': 'Tecno Smart', 'cat': 'Electrónica', 'plan': planes_obj['Básico']},
            {'schema': 'moda', 'nombre': 'Moda Express', 'cat': 'Ropa', 'plan': planes_obj['Medio']},
            {'schema': 'hogar', 'nombre': 'Hogar & Deco', 'cat': 'Hogar', 'plan': planes_obj['Profesional']}
        ]

        datos_productos = {
            'Electrónica': [
                ("Laptop Pro 14", 8500, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500"),
                ("Smartphone Z", 4200, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500"),
                ("Audífonos BT", 800, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500")
            ],
            'Ropa': [
                ("Chaqueta Jean", 350, "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=500"),
                ("Tenis Runner", 550, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"),
                ("Gorra Classic", 120, "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=500")
            ],
            'Hogar': [
                ("Silla Ergonómica", 1200, "https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=500"),
                ("Lámpara Minimal", 250, "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500"),
                ("Mesa de Centro", 800, "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=500")
            ]
        }

        clientes_data = [
            ("Juan Perez", "juan@gmail.com"),
            ("Maria Garcia", "maria@gmail.com"),
            ("Pedro Pascal", "pedro@gmail.com")
        ]

        for conf in config_tiendas:
            tenant, created = Client.objects.get_or_create(
                schema_name=conf['schema'],
                defaults={
                    'name': conf['nombre'],
                    'plan': conf['plan'],
                    'nombre_comercial': conf['nombre'],
                    'categoria_tienda': conf['cat']
                }
            )
            # Aseguramos que tenga el plan correcto (por si ya existía)
            tenant.plan = conf['plan']
            tenant.save()

            domain_url = f"{conf['schema']}.{base_domain}" if base_domain != 'localhost' else f"{conf['schema']}.localhost"
            Domain.objects.get_or_create(domain=domain_url, tenant=tenant, defaults={'is_primary': True})
            print(f"   -> Tienda {conf['nombre']} ({conf['schema']}) en Plan {conf['plan'].nombre}")

    # ---------------------------------------------------------
    # 5. POBLAR CADA TIENDA
    # ---------------------------------------------------------
    for conf in config_tiendas:
        with schema_context(conf['schema']):
            # Limpieza segura para evitar duplicados en pruebas repetidas
            Producto.objects.all().delete()
            Categoria.objects.all().delete()
            Factura.objects.all().delete()
            DetalleFactura.objects.all().delete()
            Pedido.objects.all().delete()
            CarritoItem.objects.all().delete()
            Carrito.objects.all().delete()
            TipoPago.objects.all().delete()

            cat_obj, _ = Categoria.objects.get_or_create(nombre=conf['cat'])

            prods_creados = []
            for nom, precio, img in datos_productos.get(conf['cat'], []):
                p = Producto.objects.create(
                    nombre=nom, precio=precio, stock=random.randint(10, 100),
                    categoria=cat_obj, imagen_url=img,
                    sku=f"SKU-{get_random_string(5).upper()}", activo=True
                )
                prods_creados.append(p)

            tipo_pago, _ = TipoPago.objects.get_or_create(nombre='EFECTIVO', defaults={'estado': 'ACTIVO'})

            for c_nom, c_email in clientes_data:
                cliente, _ = Cliente.objects.get_or_create(correo=c_email, defaults={'nombre': c_nom})
                
                # Crear pedidos históricos para la predicción (1 a 5 meses atrás)
                from datetime import timedelta
                from django.utils import timezone
                
                num_pedidos = random.randint(3, 8)
                for _ in range(num_pedidos):
                    p = random.choice(prods_creados)
                    cant = random.randint(1, 3)
                    
                    dias_atras = random.randint(1, 150)
                    fake_date = timezone.now() - timedelta(days=dias_atras)
                    
                    carrito = Carrito.objects.create(cliente=cliente, estado='CERRADO')
                    Carrito.objects.filter(id=carrito.id).update(fecha_creacion=fake_date)
                    
                    item = CarritoItem.objects.create(carrito=carrito, producto=p, cantidad=cant)
                    
                    pedido = Pedido.objects.create(
                        carrito=carrito,
                        estado='ENTREGADO'
                    )
                    Pedido.objects.filter(id=pedido.id).update(fecha_creacion=fake_date)
                    
                    nro_fact = f"FAC-{random.randint(10000, 99999)}"
                    factura = Factura.objects.create(
                        nro=nro_fact,
                        pedido=pedido,
                        cliente=cliente,
                        tipo_pago=tipo_pago,
                        monto_total=item.subtotal,
                        estado='VIGENTE'
                    )
                    Factura.objects.filter(nro=nro_fact).update(fecha=fake_date.date(), hora=fake_date.time())
                    
                    DetalleFactura.objects.create(
                        factura=factura,
                        producto=p,
                        cantidad=cant,
                        precio_unitario=p.precio,
                        total=item.subtotal
                    )

    print("\nSEEDER MAESTRO EJECUTADO CON ÉXITO.")
    print("   El sistema está listo con roles, permisos, planes, reportes y datos de prueba.")

if __name__ == "__main__":
    ejecutar()
