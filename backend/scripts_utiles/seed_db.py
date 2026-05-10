import os
import django
import random
import socket
from django.utils.crypto import get_random_string

# 1. Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from app_negocio.models import Categoria, Producto, Pedido, Factura
from customers.models import Client, Domain, Usuario, Rol, Plan, Cliente

def obtener_ip_dominio():
    """Detecta la IP local para usar con nip.io o lee del .env"""
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

def crear_tienda_si_no_existe(schema, nombre, categoria, base_domain, plan):
    """Crea un tenant y su dominio si no existen."""
    tenant, created = Client.objects.get_or_create(
        schema_name=schema,
        defaults={
            'name': nombre,
            'plan': plan,
            'nombre_comercial': nombre,
            'categoria_tienda': categoria,
            'descripcion': f"Tienda oficial de {nombre}."
        }
    )
    
    domain_url = f"{schema}.{base_domain}" if base_domain != 'localhost' else f"{schema}.localhost"
    Domain.objects.get_or_create(
        domain=domain_url, 
        tenant=tenant, 
        defaults={'is_primary': True}
    )
    return tenant

def ejecutar():
    print("--- 🚀 Iniciando Sincronización de Datos Procedural ---")
    base_domain = obtener_ip_dominio()
    print(f"📍 Dominio Base detectado: {base_domain}")

    # Asegurar Plan y Roles
    plan, _ = Plan.objects.get_or_create(nombre='Profesional', defaults={'precio': 99.0, 'limite_productos': 100})
    rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')

    # Configuración de Tiendas a crear/poblar
    config_tiendas = [
        {'schema': 'tecno', 'nombre': 'Tecno Smart', 'cat': 'Electrónica'},
        {'schema': 'moda', 'nombre': 'Moda Express', 'cat': 'Ropa'},
        {'schema': 'hogar', 'nombre': 'Hogar & Deco', 'cat': 'Hogar'}
    ]

    # Datos Maestros Procedurales
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
        print(f"\n📦 Procesando Tienda: {conf['nombre']} ({conf['schema']})")
        tenant = crear_tienda_si_no_existe(conf['schema'], conf['nombre'], conf['cat'], base_domain, plan)

        with schema_context(tenant.schema_name):
            # 1. Limpieza opcional
            Producto.objects.all().delete()
            Categoria.objects.all().delete()

            # 2. Categoría Principal
            cat_obj, _ = Categoria.objects.get_or_create(nombre=conf['cat'])

            # 3. Productos Procedurales
            prods_creados = []
            items = datos_productos.get(conf['cat'], [])
            for nom, precio, img in items:
                p = Producto.objects.create(
                    nombre=nom,
                    precio=precio,
                    stock=random.randint(10, 100),
                    categoria=cat_obj,
                    imagen_url=img,
                    sku=f"SKU-{get_random_string(5).upper()}",
                    activo=True
                )
                prods_creados.append(p)

            # 4. Clientes y Pedidos Completados
            for c_nom, c_email in clientes_data:
                cliente, _ = Cliente.objects.get_or_create(correo=c_email, defaults={'nombre': c_nom})
                
                # Crear 2 pedidos por cliente
                for _ in range(2):
                    p = random.choice(prods_creados)
                    pedido = Pedido.objects.create(
                        cliente=cliente,
                        total=p.precio,
                        estado='ENTREGADO',
                        direccion_envio="Av. Siempre Viva 123"
                    )
                    # Factura pagada
                    Factura.objects.create(
                        pedido=pedido,
                        total=pedido.total,
                        estado='PAGADA',
                        nro_factura=f"FAC-{random.randint(1000, 9999)}"
                    )

    print("\n✅ Sincronización finalizada. Datos maestros creados.")

if __name__ == "__main__":
    ejecutar()