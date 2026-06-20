import os
from django.core.management.base import BaseCommand
from apps.customers.models import Permiso
from django_tenants.utils import schema_context

class Command(BaseCommand):
    help = 'Crea los permisos del sistema (básicos y premium) en el esquema público.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Iniciando Seeder de Permisos ---'))

        # Los permisos siempre se guardan en el esquema público porque 'customers' es SHARED_APP.
        # Nos aseguramos de estar en el public.
        with schema_context('public'):
            
            # Lista de permisos del sistema
            permisos_data = [
                # Módulo Dashboard
                {'codigo': 'VER_DASHBOARD', 'nombre': 'Ver Dashboard', 'modulo': 'Dashboard', 'es_basico': True, 'desc': 'Acceso a la vista principal y métricas básicas'},
                {'codigo': 'VER_DASHBOARD_AVANZADO', 'nombre': 'Dashboard Avanzado', 'modulo': 'Dashboard', 'es_basico': False, 'desc': 'Métricas avanzadas, reportes y predicciones de ventas'},

                # Módulo Productos
                {'codigo': 'CREAR_PRODUCTO', 'nombre': 'Crear Productos', 'modulo': 'Productos', 'es_basico': True, 'desc': 'Permite crear nuevos productos'},
                {'codigo': 'EDITAR_PRODUCTO', 'nombre': 'Editar Productos', 'modulo': 'Productos', 'es_basico': True, 'desc': 'Permite modificar productos existentes'},
                {'codigo': 'ELIMINAR_PRODUCTO', 'nombre': 'Eliminar Productos', 'modulo': 'Productos', 'es_basico': True, 'desc': 'Permite eliminar productos'},
                {'codigo': 'GESTIONAR_INVENTARIO', 'nombre': 'Gestionar Inventario', 'modulo': 'Productos', 'es_basico': True, 'desc': 'Permite gestionar el stock de productos'},

                # Módulo Ventas / Pedidos
                {'codigo': 'VER_PEDIDOS', 'nombre': 'Ver Pedidos', 'modulo': 'Ventas', 'es_basico': True, 'desc': 'Permite listar y ver el detalle de pedidos'},
                {'codigo': 'PROCESAR_PEDIDOS', 'nombre': 'Procesar Pedidos', 'modulo': 'Ventas', 'es_basico': True, 'desc': 'Permite cambiar el estado de los pedidos y registrar envíos'},
                {'codigo': 'EMITIR_FACTURA', 'nombre': 'Emitir Facturas', 'modulo': 'Ventas', 'es_basico': True, 'desc': 'Generación de facturas para ventas'},

                # Módulo Clientes
                {'codigo': 'VER_CLIENTES', 'nombre': 'Ver Clientes', 'modulo': 'Clientes', 'es_basico': True, 'desc': 'Acceso al listado de clientes de la tienda'},
                {'codigo': 'EXPORTAR_CLIENTES', 'nombre': 'Exportar Clientes', 'modulo': 'Clientes', 'es_basico': False, 'desc': 'Permite descargar el padrón de clientes (Feature Premium)'},

                # Módulo Usuarios y Roles (Dueño de la tienda)
                {'codigo': 'GESTIONAR_USUARIOS', 'nombre': 'Gestionar Personal', 'modulo': 'Usuarios', 'es_basico': True, 'desc': 'Permite crear, editar o eliminar empleados/vendedores'},
                {'codigo': 'GESTIONAR_ROLES', 'nombre': 'Gestionar Roles', 'modulo': 'Usuarios', 'es_basico': True, 'desc': 'Permite configurar roles y permisos de los empleados'},

                # Módulo Configuración
                {'codigo': 'CONFIGURACION_TIENDA', 'nombre': 'Configuración de Tienda', 'modulo': 'Configuración', 'es_basico': True, 'desc': 'Permite editar la información de la tienda, logo y colores'},
                {'codigo': 'CONFIGURACION_PAGOS', 'nombre': 'Configuración de Pagos', 'modulo': 'Configuración', 'es_basico': False, 'desc': 'Permite vincular métodos de pago avanzados (Stripe, Paypal)'},

                # Módulo Reportes
                {'codigo': 'REP_ESTATICO', 'nombre': 'Reportes Estáticos', 'modulo': 'Reportes', 'es_basico': True, 'desc': 'Permite generar y descargar reportes predefinidos'},
                {'codigo': 'REP_DINAMICO', 'nombre': 'Reportes Dinámicos', 'modulo': 'Reportes', 'es_basico': False, 'desc': 'Permite armar reportes personalizados con métricas y agrupaciones'},
                {'codigo': 'REP_AUDIO', 'nombre': 'Reportes con IA (Voz)', 'modulo': 'Reportes', 'es_basico': False, 'desc': 'Permite realizar consultas al sistema mediante voz o lenguaje natural'},
            ]

            creados = 0
            # Limpiar permisos existentes para evitar conflictos de constraints
            Permiso.objects.all().delete()

            for p in permisos_data:
                Permiso.objects.create(
                    codigo=p['codigo'],
                    nombre=p['nombre'],
                    modulo=p['modulo'],
                    es_basico=p['es_basico'],
                    descripcion=p['desc'],
                    activo=True
                )
                creados += 1

            self.stdout.write(self.style.SUCCESS(f'[OK] Completado: {creados} permisos recreados limpiamente.'))

        # Propagar permisos a los roles de todas las tiendas existentes
        self.stdout.write(self.style.WARNING('--- Configurando roles maestros y propagando a todas las tiendas ---'))
        from apps.customers.models import Client
        from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.models.rol import Rol
        
        with schema_context('public'):
            # 1. Asegurar que existan los roles maestros
            maestro_admin, _ = Rol.objects.get_or_create(nombre='Administrador', tenant=None, defaults={'nivel': 1, 'descripcion': 'Dueño o administrador general'})
            maestro_vendedor, _ = Rol.objects.get_or_create(nombre='Vendedor', tenant=None, defaults={'nivel': 2, 'descripcion': 'Personal de ventas'})
            maestro_cliente, _ = Rol.objects.get_or_create(nombre='Cliente', tenant=None, defaults={'nivel': 3, 'descripcion': 'Comprador recurrente'})

            # 2. Asignar los permisos oficiales a cada rol maestro
            # Admin tiene todos los permisos básicos y premium aplicables a la gestión
            todos_permisos = Permiso.objects.all()
            maestro_admin.permisos.set(todos_permisos)

            # Vendedor tiene permisos limitados
            permisos_vendedor = Permiso.objects.filter(codigo__in=['VER_DASHBOARD', 'CREAR_PRODUCTO', 'EDITAR_PRODUCTO', 'VER_PEDIDOS', 'PROCESAR_PEDIDOS', 'EMITIR_FACTURA', 'VER_CLIENTES', 'REP_ESTATICO', 'REP_DINAMICO', 'REP_AUDIO'])
            maestro_vendedor.permisos.set(permisos_vendedor)

            # Cliente tiene permisos mínimos
            permisos_cliente = Permiso.objects.filter(codigo__in=['VER_PEDIDOS'])
            maestro_cliente.permisos.set(permisos_cliente)

            # 3. Reparar los Planes
            from apps.customers.tenants.models.plan import Plan
            plan_basico = Plan.objects.filter(nombre__iexact='Básico').first()
            if plan_basico:
                plan_basico.permisos.add(*Permiso.objects.filter(codigo__in=['REP_ESTATICO']))
            
            plan_medio = Plan.objects.filter(nombre__iexact='Medio').first()
            if plan_medio:
                plan_medio.permisos.add(*Permiso.objects.filter(codigo__in=['REP_ESTATICO', 'REP_DINAMICO']))
                
            plan_profesional = Plan.objects.filter(nombre__iexact='Profesional').first()
            if plan_profesional:
                plan_profesional.permisos.add(*Permiso.objects.filter(codigo__in=['REP_ESTATICO', 'REP_DINAMICO', 'REP_AUDIO']))

        for tenant in Client.objects.exclude(schema_name='public'):
            with schema_context(tenant.schema_name):
                admin_rol = Rol.objects.filter(nombre__iexact='administrador', tenant=tenant).first()
                if admin_rol:
                    admin_rol.permisos.set(maestro_admin.permisos.all())
                
                vendedor_rol = Rol.objects.filter(nombre__iexact='vendedor', tenant=tenant).first()
                if vendedor_rol:
                    vendedor_rol.permisos.set(maestro_vendedor.permisos.all())
                    
                cliente_rol = Rol.objects.filter(nombre__iexact='cliente', tenant=tenant).first()
                if cliente_rol:
                    cliente_rol.permisos.set(maestro_cliente.permisos.all())

        self.stdout.write(self.style.SUCCESS('[OK] Permisos clonados correctamente en todas las tiendas.'))
