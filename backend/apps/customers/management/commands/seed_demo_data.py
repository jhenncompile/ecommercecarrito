import os
import random
import socket
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django_tenants.utils import schema_context
from apps.customers.models import Client, Domain, Usuario, Rol, Plan, Cliente
from datetime import timedelta
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria, Producto, Pedido, Factura, Carrito, CarritoItem, DetalleFactura, TipoPago

class Command(BaseCommand):
    help = 'Genera datos de prueba procedurales: Tiendas, Productos, Clientes y Pedidos.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Iniciando Seeder Maestro Procedural ---'))

        # 1. Obtener IP/Dominio base
        base_domain = os.environ.get('REACT_APP_DOMAIN_MAIN')
        if not base_domain or base_domain == 'localhost':
            try:
                # Intenta obtener la IP local
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                base_domain = f"{ip}.nip.io"
            except Exception:
                base_domain = "localhost"
        
        self.stdout.write(f"Utilizando dominio base: {base_domain}")

        # 2. Asegurar Roles Básicos y Plan
        rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador', defaults={'descripcion': 'Acceso total'})
        # Campos reales del modelo Plan (evita crear un plan inválido/duplicado).
        # Nombre canónico 'Profesional' consistente con el seeder oficial.
        plan_pro, _ = Plan.objects.get_or_create(
            nombre='Profesional',
            defaults={
                'precio_mensual': 99.00,
                'precio_anual': 990.00,
                'max_usuarios': 999999,
                'max_productos': 999999,
            },
        )

        # 3. Datos Procedurales
        scenarios = [
            {
                'schema': 'tecnostore',
                'nombre': 'TecnoStore Bolivia',
                'cat_tienda': 'Tecnología',
                'vendedor_email': 'vendedor_tecno@gmail.com',
                'categorias': ['Celulares', 'Laptops', 'Accesorios'],
                'productos': [
                    {'n': 'iPhone 15 Pro', 'p': 8500, 'img': 'https://images.unsplash.com/photo-1696446701796-da61225697cc?w=500'},
                    {'n': 'MacBook Air M2', 'p': 10500, 'img': 'https://images.unsplash.com/photo-1611186871348-b1ec696e5237?w=500'},
                    {'n': 'Audífonos Sony XM5', 'p': 2500, 'img': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500'},
                ]
            },
            {
                'schema': 'modafashion',
                'nombre': 'Moda Fashion S.R.L.',
                'cat_tienda': 'Ropa y Accesorios',
                'vendedor_email': 'vendedor_moda@gmail.com',
                'categorias': ['Hombre', 'Mujer', 'Calzado'],
                'productos': [
                    {'n': 'Chaqueta de Cuero', 'p': 450, 'img': 'https://images.unsplash.com/photo-1551028711-03057e484991?w=500'},
                    {'n': 'Tenis Deportivos', 'p': 600, 'img': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500'},
                    {'n': 'Vestido de Gala', 'p': 1200, 'img': 'https://images.unsplash.com/photo-1539008835270-303780443390?w=500'},
                ]
            }
        ]

        clientes_nombres = ['Juan Perez', 'Maria Lopez', 'Carlos Ruiz', 'Ana Belen']

        for sc in scenarios:
            self.stdout.write(f"Configurando tienda: {sc['nombre']}...")
            
            # Crear Tenant
            tenant, created = Client.objects.get_or_create(
                schema_name=sc['schema'],
                defaults={
                    'name': sc['nombre'],
                    'plan': plan_pro,
                    'nombre_comercial': sc['nombre'],
                    'categoria_tienda': sc['cat_tienda'],
                    'descripcion': f"Bienvenido a {sc['nombre']}, lo mejor en {sc['cat_tienda']}."
                }
            )

            # Crear Dominio
            domain_url = f"{sc['schema']}.{base_domain}" if base_domain != 'localhost' else f"{sc['schema']}.localhost"
            Domain.objects.get_or_create(domain=domain_url, tenant=tenant, is_primary=True)

            # Crear Vendedor (Usuario)
            vendedor, v_created = Usuario.objects.get_or_create(
                email=sc['vendedor_email'],
                defaults={
                    'first_name': 'Vendedor',
                    'last_name': sc['schema'].capitalize(),
                    'tenant': tenant,
                    'rol': rol_admin,
                    'is_staff': True
                }
            )
            if v_created:
                vendedor.set_password('admin123')
                vendedor.save()

            # --- Llenar datos DENTRO del esquema de la tienda ---
            with schema_context(tenant.schema_name):
                # 1. Categorías
                cat_objs = []
                for c_name in sc['categorias']:
                    cat, _ = Categoria.objects.get_or_create(nombre=c_name, defaults={'descripcion': f'Productos de {c_name}'})
                    cat_objs.append(cat)

                # 2. Productos
                prod_objs = []
                for p_data in sc['productos']:
                    prod, _ = Producto.objects.get_or_create(
                        nombre=p_data['n'],
                        defaults={
                            'precio': p_data['p'],
                            'stock': random.randint(10, 50),
                            'categoria': random.choice(cat_objs),
                            'imagen_url': p_data['img'],
                            'descripcion': f'Calidad premium garantizada en {p_data["n"]}.'
                        }
                    )
                    prod_objs.append(prod)

                # 3. Clientes Públicos (Globales)
                for c_nom in clientes_nombres:
                    c_email = f"{c_nom.lower().replace(' ', '.')}@example.com"
                    cliente, c_created = Cliente.objects.get_or_create(
                        correo=c_email,
                        defaults={'nombre': c_nom, 'telefono': '70012345'}
                    )
                    if c_created:
                        cliente.set_password('cliente123')

                    # 4. Crear Historial de Pedidos para este cliente
                    if random.choice([True, False]): # Solo algunos tienen pedidos
                        num_pedidos = random.randint(3, 8)
                        for i in range(num_pedidos):
                            # Fecha aleatoria entre 1 y 150 días atrás (para tener varios periodos)
                            dias_atras = random.randint(1, 150)
                            fake_date = timezone.now() - timedelta(days=dias_atras)

                            # 4.1 Carrito
                            carrito = Carrito.objects.create(
                                cliente=cliente,
                                estado='CERRADO'
                            )
                            Carrito.objects.filter(id=carrito.id).update(fecha_creacion=fake_date)

                            # 4.2 Items del Carrito
                            num_items = random.randint(1, 3)
                            total_pedido = 0
                            items_creados = []
                            for _ in range(num_items):
                                prod = random.choice(prod_objs)
                                cant = random.randint(1, 3)
                                total_item = prod.precio * cant
                                total_pedido += total_item
                                item = CarritoItem.objects.create(
                                    carrito=carrito,
                                    producto=prod,
                                    cantidad=cant
                                )
                                items_creados.append((item, prod, cant, prod.precio, total_item))

                            # 4.3 Pedido
                            pedido = Pedido.objects.create(
                                carrito=carrito,
                                estado='ENTREGADO',
                                observaciones='Pedido histórico generado'
                            )
                            Pedido.objects.filter(id=pedido.id).update(fecha_creacion=fake_date)

                            # 4.4 Tipo Pago
                            tipo_pago, _ = TipoPago.objects.get_or_create(nombre='EFECTIVO', defaults={'estado': 'ACTIVO'})

                            # 4.5 Factura
                            nro_fact = f"F-{random.randint(10000, 99999)}"
                            factura = Factura.objects.create(
                                nro=nro_fact,
                                pedido=pedido,
                                cliente=cliente,
                                tipo_pago=tipo_pago,
                                monto_total=total_pedido,
                                estado='VIGENTE'
                            )
                            Factura.objects.filter(nro=nro_fact).update(fecha=fake_date.date(), hora=fake_date.time())

                            # 4.6 Detalles de Factura
                            for item, prod, cant, p_unitario, t_item in items_creados:
                                DetalleFactura.objects.create(
                                    factura=factura,
                                    producto=prod,
                                    cantidad=cant,
                                    precio_unitario=p_unitario,
                                    total=t_item
                                )

        self.stdout.write(self.style.SUCCESS('--- Seeder Finalizado Exitosamente ---'))
        self.stdout.write("Acceso Vendedores: admin123")
        self.stdout.write("Acceso Clientes: cliente123")
