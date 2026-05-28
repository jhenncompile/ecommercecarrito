#!/usr/bin/env python
# ========================================================================
# SCRIPT DE SEEDERS V5.4 - ESTRUCTURA DE NEGOCIO REAL
# ========================================================================
# Corregidos modelos: Plan, Carrito, Pedido y Factura.

import os
import sys
import random
import socket
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
from apps.customers.models import Client, Domain, Usuario, Rol, Plan, Cliente
from apps.negocio.models import Producto, Categoria, Pedido, Factura, Carrito, CarritoItem, TipoPago

fake = Faker(['es_ES', 'es_MX'])

class BusinessGenerator:
    PASSWORD_STANDAR = "Password123!"
    
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

    def ejecutar_sincronizacion(self, n_tiendas, n_clientes, p_por_tienda, o_por_cliente):
        print(f"\n--- âš¡ Motor Especializado V5.4 ---")

        with schema_context('public'):
            # 1. Crear o asegurar los planes oficiales de la plataforma
            plan_basico, _ = Plan.objects.get_or_create(
                nombre='basico', 
                defaults={'precio_mensual': 0.0, 'precio_anual': 0.0, 'max_usuarios': 1, 'max_productos': 50}
            )
            plan_profesional, _ = Plan.objects.get_or_create(
                nombre='profesional', 
                defaults={'precio_mensual': 29.0, 'precio_anual': 290.0, 'max_usuarios': 5, 'max_productos': 1000}
            )
            plan_premium, _ = Plan.objects.get_or_create(
                nombre='premium', 
                defaults={'precio_mensual': 99.0, 'precio_anual': 990.0, 'max_usuarios': 50, 'max_productos': 5000}
            )
            
            # El plan por defecto para las tiendas de prueba
            plan_maestro, _ = Plan.objects.get_or_create(
                nombre='Plan Maestro', 
                defaults={'precio_mensual': 150.0, 'precio_anual': 1500.0, 'max_usuarios': 50, 'max_productos': 5000}
            )
            
            # Roles globales (aunque en este sistema multi-tenant los roles se crean por tenant)
            rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador', tenant=None)

        # 1. Nuevas Tiendas
        if n_tiendas > 0:
            for _ in range(n_tiendas):
                nombre = fake.company()
                schema = f"shop_{fake.unique.user_name()}"[:20].replace('.', '_').lower()
                with schema_context('public'):
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
        todas = Client.objects.exclude(schema_name='public')
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
        todos_clientes = Cliente.objects.all()
        for cliente in todos_clientes:
            for _ in range(o_por_cliente):
                t_destino = random.choice(todas)
                with tenant_context(t_destino):
                    prods = list(Producto.objects.filter(activo=True))
                    if prods:
                        # FLUJO REAL: Carrito -> Pedido -> Factura
                        carrito = Carrito.objects.create(cliente=cliente, estado='CERRADO')
                        p = random.choice(prods)
                        CarritoItem.objects.create(carrito=carrito, producto=p, cantidad=1)
                        
                        pedido = Pedido.objects.create(carrito=carrito, estado='ENTREGADO')
                        
                        Factura.objects.create(
                            nro=f"FAC-{get_random_string(10).upper()}",
                            pedido=pedido,
                            cliente=cliente,
                            tipo_pago=TipoPago.objects.first(),
                            monto_total=p.precio,
                            estado='VIGENTE'
                        )
        print(f"\nâœ¨ Sincronización Finalizada.")

def main():
    seeder = DatabaseSeeder()
    try:
        nt = int(input("Â¿Tiendas nuevas? [0]: ") or 0)
        nc = int(input("Â¿Clientes nuevos? [0]: ") or 0)
        pp = int(input("Â¿Productos A AÑADIR por tienda? [10]: ") or 10)
        op = int(input("Â¿Pedidos A GENERAR por cliente? [2]: ") or 2)
        seeder.ejecutar_sincronizacion(nt, nc, pp, op)
    except KeyboardInterrupt: pass
    except Exception as e: print(f"Error: {e}"); import traceback; traceback.print_exc()

if __name__ == '__main__': main()

