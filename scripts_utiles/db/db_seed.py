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

from django_tenants.utils import tenant_context, schema_context
from django.utils import timezone
from apps.customers.models import Client, Domain, Usuario, Rol, Plan, Cliente
from apps.negocio.models import Producto, Categoria, Pedido, Factura, Carrito, CarritoItem, TipoPago

fake = Faker(['es_ES', 'es_MX'])

class BusinessGenerator:
    PASSWORD_STANDAR = "Password123!"
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
            raw_name = fake.unique.user_name().lower()
            clean_name = re.sub(r'[^a-z0-9]+', '', raw_name)
            if not clean_name:
                clean_name = get_random_string(8, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')

            schema = f"shop{clean_name}"[:20]
            if not Client.objects.filter(schema_name=schema).exists():
                return schema

        return f"shop{get_random_string(12, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')}"

    @staticmethod
    def dias_periodo_pedidos(codigo):
        codigo_normalizado = (codigo or '1m').strip().lower()
        if codigo_normalizado not in BusinessGenerator.PERIODOS_PEDIDOS_DIAS:
            print("  [i] Periodo inválido. Usando 1m por defecto.")
            codigo_normalizado = '1m'

        return BusinessGenerator.PERIODOS_PEDIDOS_DIAS[codigo_normalizado]

    @staticmethod
    def fecha_aleatoria_pedido(dias_atras):
        ahora = timezone.now()
        segundos_atras = random.randint(0, max(1, dias_atras * 24 * 60 * 60))
        return ahora - timedelta(seconds=segundos_atras)

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

    def ejecutar_sincronizacion(self, n_tiendas, n_clientes, p_por_tienda, o_por_cliente, periodo_pedidos='1m'):
        print(f"\n--- âš¡ Motor Especializado V5.4 ---")
        dias_pedidos = BusinessGenerator.dias_periodo_pedidos(periodo_pedidos)

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
            # 1. Crear o asegurar los planes oficiales de la plataforma
            plan_basico, _ = Plan.objects.get_or_create(
                nombre='Básico', 
                defaults={'precio_mensual': 29.0, 'precio_anual': 290.0, 'max_usuarios': 2, 'max_productos': 50}
            )
            plan_basico.permisos.set([permisos_obj['REP_ESTATICO']])

            plan_profesional, _ = Plan.objects.get_or_create(
                nombre='Profesional', 
                defaults={'precio_mensual': 99.0, 'precio_anual': 990.0, 'max_usuarios': 20, 'max_productos': 5000}
            )
            plan_profesional.permisos.set([permisos_obj['REP_ESTATICO'], permisos_obj['REP_DINAMICO'], permisos_obj['REP_AUDIO']])

            plan_medio, _ = Plan.objects.get_or_create(
                nombre='Medio', 
                defaults={'precio_mensual': 59.0, 'precio_anual': 590.0, 'max_usuarios': 5, 'max_productos': 500}
            )
            plan_medio.permisos.set([permisos_obj['REP_ESTATICO'], permisos_obj['REP_DINAMICO']])
            
            # Roles globales (aunque en este sistema multi-tenant los roles se crean por tenant)
            rol_admin = Rol.objects.get(nombre='Administrador', tenant=None)

        # 1. Nuevas Tiendas
        if n_tiendas > 0:
            for _ in range(n_tiendas):
                nombre = fake.company()
                with schema_context('public'):
                    schema = BusinessGenerator.schema_tienda_seguro()
                    tenant, _ = Client.objects.get_or_create(schema_name=schema, defaults={'name': nombre, 'plan': plan_profesional, 'nombre_comercial': nombre, 'categoria_tienda': fake.job()})
                    Domain.objects.get_or_create(domain=f"{schema}.{self.base_domain}" if self.base_domain != 'localhost' else f"{schema}.localhost", tenant=tenant, defaults={'is_primary': True})
                    user = Usuario.objects.create_user(email=f"admin@{schema}.local", password=BusinessGenerator.PASSWORD_STANDAR, tenant=tenant, is_staff=True)
                    user.roles.add(rol_admin)

        # 2. Nuevos Clientes
        if n_clientes > 0:
            with schema_context('public'):
                for _ in range(n_clientes):
                    c, created = Cliente.objects.get_or_create(correo=fake.unique.email(), defaults={'nombre': fake.name()})
                    if created: c.set_password(BusinessGenerator.PASSWORD_STANDAR); c.save()

        # 3. Poblar TODAS (OG + Nuevas)
        todas = list(Client.objects.exclude(schema_name='public'))
        all_cat_names = list(BusinessGenerator.KEYWORDS_POR_CATEGORIA.keys())

        for tenant in todas:
            with tenant_context(tenant):
                # Especialización
                tienda_cats = random.sample(all_cat_names, random.randint(1, 3))
                cat_objects = [Categoria.objects.get_or_create(nombre=cn)[0] for cn in tienda_cats]
                for _ in range(p_por_tienda):
                    Producto.objects.create(**BusinessGenerator.random_product_data(random.choice(cat_objects)))
                
                # Asegurar TipoPago
                tp, _ = TipoPago.objects.get_or_create(nombre='Efectivo')
                print(f"  âœ… {tenant.schema_name}: +{p_por_tienda} productos.")

        # 4. Pedidos Globales
        if o_por_cliente > 0 and not todas:
            print("  [i] No hay tiendas disponibles. Se omite generación de pedidos.")
            print(f"\nâœ¨ Sincronización Finalizada.")
            return

        if o_por_cliente > 0:
            print(f"\n🧾 4. Generando pedidos aleatorios de los últimos {dias_pedidos} días...")
            print(f"  Estados posibles: {', '.join(BusinessGenerator.ESTADOS_PEDIDO_VENTA)}")

        todos_clientes = Cliente.objects.all()
        for cliente in todos_clientes:
            for _ in range(o_por_cliente):
                t_destino = random.choice(todas)
                with tenant_context(t_destino):
                    prods = list(Producto.objects.filter(activo=True))
                    if prods:
                        fecha_pedido = BusinessGenerator.fecha_aleatoria_pedido(dias_pedidos)
                        estado_pedido = random.choice(BusinessGenerator.ESTADOS_PEDIDO_VENTA)

                        # FLUJO REAL: Carrito -> Pedido -> Factura
                        carrito = Carrito.objects.create(cliente=cliente, estado='CERRADO')
                        p = random.choice(prods)
                        item = CarritoItem.objects.create(carrito=carrito, producto=p, cantidad=random.randint(1, 4))
                        
                        pedido = Pedido.objects.create(carrito=carrito, estado=estado_pedido)
                        
                        factura = Factura.objects.create(
                            nro=f"FAC-{get_random_string(10).upper()}",
                            pedido=pedido,
                            cliente=cliente,
                            tipo_pago=TipoPago.objects.first(),
                            monto_total=p.precio * item.cantidad,
                            estado='VIGENTE'
                        )

                        Carrito.objects.filter(pk=carrito.pk).update(
                            fecha_creacion=fecha_pedido,
                            fecha_actualizacion=fecha_pedido
                        )
                        CarritoItem.objects.filter(pk=item.pk).update(fecha_agregado=fecha_pedido)
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
        periodo = input("Â¿Desde cuánto tiempo atrás generar pedidos? [1m] (1a=1 año, 1m=1 mes, 1s=1 semana): ") or '1m'
        seeder.ejecutar_sincronizacion(nt, nc, pp, op, periodo)
    except KeyboardInterrupt: pass
    except Exception as e: print(f"Error: {e}"); import traceback; traceback.print_exc()

if __name__ == '__main__': main()

