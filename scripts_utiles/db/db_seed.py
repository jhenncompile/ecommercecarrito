#!/usr/bin/env python
# ========================================================================
# SCRIPT DE SEEDERS V5.4 - ESTRUCTURA DE NEGOCIO REAL
# ========================================================================
# Corregidos modelos: Plan, Carrito, Pedido y Factura.

import os
import sys
import random
import socket
import re
from datetime import timedelta
from pathlib import Path
from django.utils.crypto import get_random_string
from django.core.management import call_command
from django.db import connection

# Configuración de Rutas
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

try:
    from faker import Faker
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "faker"])
    from faker import Faker

from django_tenants.utils import tenant_context, schema_context, schema_exists
from django.utils import timezone
from apps.customers.models import Client, Domain, Usuario, Rol, Plan, Cliente
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito import Carrito
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito_item import CarritoItem
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.models.tipo_pago import TipoPago
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.detalle_factura import DetalleFactura
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.factura import Factura

fake = Faker(['es_ES', 'es_MX'])

class BusinessGenerator:
    PASSWORD_STANDAR = "Pass123@"
    ESTADOS_PEDIDO_VENTA = ['PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO']
    PERIODOS_PEDIDOS_DIAS = {
        '1a': 365,
        '1m': 30,
        '1s': 7,
    }
    
    KEYWORDS_POR_CATEGORIA = {
        'Electrónica': ['pro', 'procesador', 'digital', 'inteligente', 'batería', 'conexión', 'velocidad', 'tech', 'pantalla', 'inalámbrico', 'bluetooth', 'wifi', 'sensor', 'circuito', 'voltaje', 'corriente', 'usb', 'hdmi', 'led', 'audio', 'cámara', 'resolución', 'memoria', 'almacenamiento', 'carga', 'cable', 'microcontrolador', 'placa', 'amplificador', 'frecuencia', 'portátil', 'gadget'],
        'Moda': ['algodón', 'tela', 'diseño', 'estilo', 'elegante', 'confort', 'tendencia', 'ropa', 'vestido', 'camisa', 'pantalón', 'zapatos', 'talla', 'costura', 'casual', 'formal', 'urbano', 'temporada', 'invierno', 'verano', 'accesorios', 'cuero', 'denim', 'boutique', 'calzado', 'chaqueta', 'abrigo', 'textil', 'estampado', 'moda'],
        'Hogar': ['decoración', 'madera', 'interior', 'moderno', 'calidad', 'duradero', 'confort', 'casa', 'mueble', 'sofá', 'iluminación', 'cocina', 'baño', 'jardín', 'limpieza', 'organización', 'espacio', 'minimalista', 'cerámica', 'vidrio', 'electrodoméstico', 'descanso', 'cama', 'almohada', 'sala', 'comedor', 'terraza', 'climatización', 'hogar'],
        'Salud': ['vital', 'natural', 'orgánico', 'bienestar', 'cuidado', 'suplemento', 'fit', 'vitaminas', 'nutrición', 'piel', 'higiene', 'medicina', 'terapia', 'relajación', 'saludable', 'vegano', 'proteína', 'dieta', 'cuerpo', 'mente', 'clínico', 'prevención', 'antioxidante', 'colágeno', 'hidratación', 'metabolismo', 'farmacia'],
        'Deportes': ['rendimiento', 'fuerza', 'entrenamiento', 'atlético', 'deporte', 'dinámico', 'gimnasio', 'fitness', 'cardio', 'resistencia', 'flexibilidad', 'muscular', 'zapatillas', 'pelota', 'bicicleta', 'natación', 'correr', 'yoga', 'pesas', 'competición', 'outdoor', 'rutina', 'suplementación', 'ciclismo', 'maratón', 'cancha', 'equipo'],
        'Informática y Redes': ['servidor', 'router', 'switch', 'nube', 'software', 'hardware', 'código', 'datos', 'red', 'hosting', 'vps', 'programación', 'sistema', 'computadora', 'laptop', 'teclado', 'ratón', 'monitor', 'almacenamiento', 'ssd', 'lan', 'proxy', 'base de datos', 'linux'],
        'Videojuegos': ['consola', 'pc', 'gamer', 'multijugador', 'aventura', 'acción', 'rpg', 'gráficos', 'mando', 'headset', 'streaming', 'fps', 'indie', 'logros', 'virtual', 'arcade', 'narrativo', 'simulador', 'online', 'launcher', 'mod'],
        'Herramientas y Bricolaje': ['taladro', 'destornillador', 'soldador', 'medición', 'tester', 'crimpadora', 'pinzas', 'taller', 'reparación', 'mantenimiento', 'voltímetro', 'tornillo', 'tuerca', 'llave', 'martillo', 'sierra', 'bricolaje', 'industrial', 'precisión']
    }

    @staticmethod
    def obtener_ip_dominio():
        base_domain = os.environ.get('REACT_APP_DOMAIN_MAIN')
        if not base_domain or base_domain == 'localhost' or '192.168' in base_domain:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return f"{ip}.nip.io"
            except Exception: return "localhost"
        return base_domain

    @staticmethod
    def schema_tienda_seguro():
        for _ in range(100):
            raw_name = fake.unique.company()
            # Convert to camelCase and remove special chars
            parts = re.split(r'[^a-zA-Z0-9]+', raw_name)
            parts = [p for p in parts if p]
            if not parts:
                clean_name = get_random_string(8, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            else:
                clean_name = parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])

            schema = f"shop{clean_name}"[:20]
            if not Client.objects.filter(schema_name=schema).exists():
                return schema

        return f"shop{get_random_string(12, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')}"

    @staticmethod
    def parse_rango_fechas(entrada):
        from datetime import datetime
        ahora = timezone.now()
        entrada = (entrada or '1m').strip().lower()
        
        if entrada in BusinessGenerator.PERIODOS_PEDIDOS_DIAS:
            dias = BusinessGenerator.PERIODOS_PEDIDOS_DIAS[entrada]
            return ahora - timedelta(days=dias), ahora

        partes = entrada.split()
        try:
            if len(partes) == 1:
                y = int(partes[0])
                return timezone.make_aware(datetime(y, 1, 1)), timezone.make_aware(datetime(y, 12, 31, 23, 59, 59))
            elif len(partes) == 2:
                y1, y2 = map(int, partes)
                return timezone.make_aware(datetime(y1, 1, 1)), timezone.make_aware(datetime(y2, 12, 31, 23, 59, 59))
            elif len(partes) == 3:
                d, m, y = map(int, partes)
                return timezone.make_aware(datetime(y, m, d)), ahora
            elif len(partes) == 6:
                d1, m1, y1, d2, m2, y2 = map(int, partes)
                return timezone.make_aware(datetime(y1, m1, d1)), timezone.make_aware(datetime(y2, m2, d2, 23, 59, 59))
        except Exception as e:
            print(f"  [i] Error al parsear fecha ({e}). Usando 1m por defecto.")
        
        return ahora - timedelta(days=30), ahora

    @staticmethod
    def fecha_aleatoria_rango(start, end):
        delta = end - start
        int_delta = int(delta.total_seconds())
        if int_delta <= 0: return start
        return start + timedelta(seconds=random.randint(0, int_delta))

    @staticmethod
    def random_product_data(categoria_obj):
        cat_nombre = categoria_obj.nombre
        kws = BusinessGenerator.KEYWORDS_POR_CATEGORIA.get(cat_nombre, [fake.word() for _ in range(3)])
        kw_principal = random.choice(kws).capitalize()
        kw_desc = " ".join(random.sample(kws, min(len(kws), 5)))
        adjetivos = ["Pro", "Ultra", "Max", "Lite", "Edition", "Master"]
        nombre = f"{kw_principal} {random.choice(adjetivos)} {get_random_string(3).upper()}"
        return {
            'nombre': nombre,
            'sku': f"SKU-{get_random_string(8).upper()}",
            'precio': round(random.uniform(50, 4500), 2),
            'stock': random.randint(0, 100),
            'categoria': categoria_obj,
            'activo': True,
            'descripcion': f"{fake.sentence()} {kw_desc}. Calidad superior para {cat_nombre}.",
            'imagen_url': f"https://picsum.photos/seed/{get_random_string(5)}/500/500"
        }

class DatabaseSeeder:
    def __init__(self):
        self.base_domain = BusinessGenerator.obtener_ip_dominio()

    def sync_tenant_schema(self, tenant):
        if not schema_exists(tenant.schema_name):
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA {connection.ops.quote_name(tenant.schema_name)}')
            connection.set_schema_to_public()
        call_command(
            'migrate_schemas',
            tenant=True,
            schema_name=tenant.schema_name,
            run_syncdb=True,
            interactive=False,
            verbosity=0,
        )

    def get_or_create_tenant(self, schema, defaults):
        tenant = Client.objects.filter(schema_name=schema).first()
        created = tenant is None
        if created:
            tenant = Client(schema_name=schema, **defaults)
            tenant.auto_create_schema = False
            tenant.save()
        else:
            for field, value in defaults.items():
                setattr(tenant, field, value)
            tenant.auto_create_schema = False
            tenant.save()

        self.sync_tenant_schema(tenant)
        return tenant, created

    def ensure_tenant_admin(self, tenant, rol_admin):
        user, created = Usuario.objects.get_or_create(
            email=f"admin@{tenant.schema_name}.com",
            defaults={'tenant': tenant, 'is_staff': True},
        )
        if created:
            user.set_password(BusinessGenerator.PASSWORD_STANDAR)
        user.tenant = tenant
        user.is_staff = True
        user.save()
        user.roles.add(rol_admin)
        return user

    def ejecutar_sincronizacion(self, n_tiendas, n_clientes, p_por_tienda, o_por_cliente, periodo_pedidos='1m'):
        print(f"\n--- ⚡ Motor Especializado V5.4 ---")
        fecha_inicio, fecha_fin = BusinessGenerator.parse_rango_fechas(periodo_pedidos)

        with schema_context('public'):
            print("\n🔑 1. Configurando Permisos Maestros y de Reportes...")
            permisos_data = [
                ("Acceso Total Sistema", "SYS_ALL", "Sistema", True, "Acceso irrestricto"),
                ("Gestionar Tenants", "SYS_TENANTS", "Sistema", True, "Crear y eliminar tiendas"),
                ("Gestionar Productos", "STORE_PRODUCTS", "Inventario", True, "Gestionar productos"),
                ("Gestionar Ventas", "STORE_SALES", "Ventas", True, "Procesar facturas"),
                ("Ver Reportes", "STORE_REPORTS", "Análisis", True, "Ver métricas"),
                ("Realizar Compras", "CLIENT_BUY", "Tienda", True, "Pagar"),
                ("Ver Historial", "CLIENT_HISTORY", "Tienda", True, "Ver pedidos"),
                ("Reportes Estáticos", "REP_ESTATICO", "Reportes", True, "Generar reportes predefinidos"),
                ("Reportes Dinámicos", "REP_DINAMICO", "Reportes", False, "Armar reportes personalizados"),
                ("Reportes con IA (Voz)", "REP_AUDIO", "Reportes", False, "Consultas mediante voz"),
            ]
            
            from apps.customers.models import Permiso
            permisos_obj = {}
            for nombre, codigo, modulo, es_basico, desc in permisos_data:
                p, _ = Permiso.objects.get_or_create(
                    codigo=codigo,
                    defaults={'nombre': nombre, 'modulo': modulo, 'es_basico': es_basico, 'descripcion': desc, 'activo': True}
                )
                permisos_obj[codigo] = p

            print("👥 2. Configurando Roles y asginando Permisos...")
            roles_data = [
                ("Administrador", 1, ["SYS_ALL", "SYS_TENANTS", "STORE_PRODUCTS", "STORE_SALES", "STORE_REPORTS", "REP_ESTATICO", "REP_DINAMICO", "REP_AUDIO"]),
                ("Vendedor", 2, ["STORE_PRODUCTS", "STORE_SALES", "STORE_REPORTS", "REP_ESTATICO", "REP_DINAMICO", "REP_AUDIO"]),
                ("Cliente", 3, ["CLIENT_BUY", "CLIENT_HISTORY"]),
            ]
            for nombre_rol, nivel, codigos in roles_data:
                rol, _ = Rol.objects.get_or_create(nombre=nombre_rol, tenant=None, defaults={'nivel': nivel, 'activo': True})
                rol.permisos.set([permisos_obj[c] for c in codigos if c in permisos_obj])

            print("💳 3. Configurando Planes SaaS y sus Reportes...")
            # 1. Crear o asegurar los 4 nuevos planes oficiales
            plan_gratis, _ = Plan.objects.get_or_create(
                nombre='Gratis', 
                defaults={'precio_mensual': 0.0, 'precio_anual': 0.0, 'max_usuarios': 2, 'max_productos': 50, 'facturacion_max': 1000.0}
            )
            plan_gratis.permisos.set([])

            plan_standard, _ = Plan.objects.get_or_create(
                nombre='Standard', 
                defaults={'precio_mensual': 29.0, 'precio_anual': 290.0, 'max_usuarios': 5, 'max_productos': 500, 'facturacion_max': 10000.0}
            )
            plan_standard.permisos.set([permisos_obj['REP_ESTATICO']])

            plan_gold, _ = Plan.objects.get_or_create(
                nombre='Gold', 
                defaults={'precio_mensual': 69.0, 'precio_anual': 690.0, 'max_usuarios': 15, 'max_productos': 5000, 'facturacion_max': 500000.0}
            )
            # Faltan algunos permisos premium que crea el fix, pero el seeder base usa estos:
            plan_gold.permisos.set([permisos_obj['REP_ESTATICO']])

            plan_profesional, _ = Plan.objects.get_or_create(
                nombre='Profesional', 
                defaults={'precio_mensual': 99.0, 'precio_anual': 990.0, 'max_usuarios': 999999, 'max_productos': 999999, 'facturacion_max': None}
            )
            plan_profesional.permisos.set([permisos_obj['REP_ESTATICO'], permisos_obj['REP_DINAMICO'], permisos_obj['REP_AUDIO']])
            
            # Fuerza a actualizar los límites en la base de datos por si get_or_create encontró un plan viejo con 0
            Plan.objects.filter(id=plan_gratis.id).update(max_usuarios=2, max_productos=50)
            Plan.objects.filter(id=plan_standard.id).update(max_usuarios=5, max_productos=500)
            Plan.objects.filter(id=plan_gold.id).update(max_usuarios=15, max_productos=5000)
            Plan.objects.filter(id=plan_profesional.id).update(max_usuarios=999999, max_productos=999999)
            
            todos_los_planes = [plan_gratis, plan_standard, plan_gold, plan_profesional]
            # Roles globales (aunque en este sistema multi-tenant los roles se crean por tenant)
            rol_admin = Rol.objects.get(nombre='Administrador', tenant=None)

        # 1. Nuevas Tiendas
        if n_tiendas > 0:
            for _ in range(n_tiendas):
                nombre = fake.company()
                with schema_context('public'):
                    schema = BusinessGenerator.schema_tienda_seguro()
                    plan_aleatorio = random.choice(todos_los_planes)
                    tenant, _ = self.get_or_create_tenant(
                        schema,
                        {
                            'name': nombre,
                            'plan': plan_aleatorio,
                            'nombre_comercial': nombre,
                            'categoria_tienda': fake.job(),
                        },
                    )
                    Domain.objects.get_or_create(domain=f"{schema}.{self.base_domain}" if self.base_domain != 'localhost' else f"{schema}.localhost", tenant=tenant, defaults={'is_primary': True})
                    self.ensure_tenant_admin(tenant, rol_admin)

        # 2. Nuevos Clientes
        if n_clientes > 0:
            with schema_context('public'):
                for _ in range(n_clientes):
                    nombre_cliente = fake.name()
                    nombre_limpio = re.sub(r'[^a-z0-9]', '', nombre_cliente.lower().split()[0])
                    dominio_limpio = random.choice(['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 'mail.com'])
                    sufijo = random.randint(10, 9999)
                    correo_cliente = f"{nombre_limpio}{sufijo}@{dominio_limpio}"
                    c, created = Cliente.objects.get_or_create(correo=correo_cliente, defaults={'nombre': nombre_cliente})
                    if created: c.set_password(BusinessGenerator.PASSWORD_STANDAR); c.save()

        # 3. Poblar TODAS (OG + Nuevas)
        todas = list(Client.objects.exclude(schema_name='public'))
        all_cat_names = list(BusinessGenerator.KEYWORDS_POR_CATEGORIA.keys())

        for tenant in todas:
            self.sync_tenant_schema(tenant)
            self.ensure_tenant_admin(tenant, rol_admin)

        for tenant in todas:
            with tenant_context(tenant):
                # Especialización
                tienda_cats = random.sample(all_cat_names, random.randint(1, 3))
                cat_objects = [Categoria.objects.get_or_create(nombre=cn)[0] for cn in tienda_cats]
                creados = 0
                for _ in range(p_por_tienda):
                    try:
                        Producto.objects.create(**BusinessGenerator.random_product_data(random.choice(cat_objects)))
                        creados += 1
                    except Exception as e:
                        print(f"  [!] Producto omitido en '{tenant.schema_name}' (posible límite de plan): {e}")
                        break
                
                # Asegurar TipoPago
                tp, _ = TipoPago.objects.get_or_create(nombre='Efectivo')
                print(f"  ✅ {tenant.schema_name}: +{creados} productos.")

        # 4. Pedidos Globales
        if o_por_cliente > 0 and not todas:
            print("  [i] No hay tiendas disponibles. Se omite generación de pedidos.")
            print(f"\n✨ Sincronización Finalizada.")
            return

        if o_por_cliente > 0:
            print(f"\n🧾 4. Generando {o_por_cliente} pedidos por cliente EN CADA TIENDA entre {fecha_inicio.strftime('%d/%m/%Y')} y {fecha_fin.strftime('%d/%m/%Y')}...")
            print(f"  Estados posibles: {', '.join(BusinessGenerator.ESTADOS_PEDIDO_VENTA)}")

        todos_clientes = list(Cliente.objects.all())
        from django.db import transaction

        for t_destino in todas:
            with tenant_context(t_destino):
                if o_por_cliente <= 0:
                    continue
                prods = list(Producto.objects.filter(activo=True))
                if not prods:
                    continue
                
                print(f"  -> {t_destino.schema_name}: Generando transacciones para {len(todos_clientes)} clientes...")
                for cliente in todos_clientes:
                    with transaction.atomic():
                        for _ in range(o_por_cliente):
                            fecha_pedido = BusinessGenerator.fecha_aleatoria_rango(fecha_inicio, fecha_fin)
                            estado_pedido = random.choice(BusinessGenerator.ESTADOS_PEDIDO_VENTA)

                            # FLUJO REAL: Carrito -> Pedido -> Factura
                            # Elegir entre 1 y 3 productos DISTINTOS por carrito
                            # (pesos: 40% solo 1 producto, 40% dos, 20% tres)
                            n_prods = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
                            prods_pedido = random.sample(prods, min(n_prods, len(prods)))

                            carrito = Carrito.objects.create(cliente=cliente, estado='CERRADO')

                            items_creados = []
                            monto_total = 0
                            for p in prods_pedido:
                                cantidad = random.randint(1, 3)
                                item = CarritoItem.objects.create(
                                    carrito=carrito, producto=p, cantidad=cantidad
                                )
                                items_creados.append((item, p, cantidad))
                                monto_total += p.precio * cantidad

                            pedido = Pedido.objects.create(carrito=carrito, estado=estado_pedido)

                            factura = Factura.objects.create(
                                nro=f"FAC-{get_random_string(10).upper()}",
                                pedido=pedido,
                                cliente=cliente,
                                tipo_pago=TipoPago.objects.first(),
                                monto_total=monto_total,
                                estado='VIGENTE'
                            )

                            for item, p, cantidad in items_creados:
                                DetalleFactura.objects.create(
                                    factura=factura,
                                    producto=p,
                                    cantidad=cantidad,
                                    precio_unitario=p.precio,
                                    total=p.precio * cantidad
                                )
                                CarritoItem.objects.filter(pk=item.pk).update(fecha_agregado=fecha_pedido)

                            Carrito.objects.filter(pk=carrito.pk).update(
                                fecha_creacion=fecha_pedido,
                                fecha_actualizacion=fecha_pedido
                            )
                            Pedido.objects.filter(pk=pedido.pk).update(
                                fecha_creacion=fecha_pedido,
                                fecha_actualizacion=fecha_pedido
                            )
                            Factura.objects.filter(pk=factura.pk).update(
                                fecha=fecha_pedido.date(),
                                hora=fecha_pedido.time()
                            )
        print(f"\nâœ¨ Sincronización Finalizada.")

def main():
    seeder = DatabaseSeeder()
    try:
        nt = int(input("Â¿Tiendas nuevas? [0]: ") or 0)
        nc = int(input("Â¿Clientes nuevos? [0]: ") or 0)
        pp = int(input("Â¿Productos A AÑADIR por tienda? [10]: ") or 10)
        op = int(input("Â¿Pedidos A GENERAR por cliente? [2]: ") or 2)
        periodo = input("¿Rango de fechas para pedidos? [1a (1 año)]\n  (Formatos: '1m', '1a', '2002', '2002 2026', '18 12 2002', '18 12 2002 12 12 2026'): ") or '1a'
        seeder.ejecutar_sincronizacion(nt, nc, pp, op, periodo)
    except KeyboardInterrupt: pass
    except Exception as e: print(f"Error: {e}"); import traceback; traceback.print_exc()

if __name__ == '__main__': main()

