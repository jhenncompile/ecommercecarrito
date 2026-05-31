import os
import sys
import django
from pathlib import Path

# Configurar Django
PROJECT_ROOT = Path(__file__).resolve().parent.parent / 'backend'
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from apps.customers.models import Client
from apps.customers.users.models.rol import Rol

print("Iniciando reparación de roles en todos los tenants...")

# Obtener roles maestros del schema public
with schema_context('public'):
    maestro_admin = Rol.objects.filter(nombre='Administrador', tenant__isnull=True).first()
    maestro_vendedor = Rol.objects.filter(nombre='Vendedor', tenant__isnull=True).first()
    maestro_cliente = Rol.objects.filter(nombre='Cliente', tenant__isnull=True).first()

if not maestro_admin:
    print("Error: No se encontraron los roles maestros en public. Ejecuta el seeder primero.")
    sys.exit(1)

for tenant in Client.objects.exclude(schema_name='public'):
    print(f"\nProcesando tenant: {tenant.schema_name}")
    with schema_context(tenant.schema_name):
        # Admin
        admin_rol = Rol.objects.filter(nombre__iexact='administrador', tenant=tenant).first()
        if admin_rol:
            admin_rol.permisos.set(maestro_admin.permisos.all())
            print("  - Permisos de Administrador actualizados.")
        
        # Vendedor
        vendedor_rol = Rol.objects.filter(nombre__iexact='vendedor', tenant=tenant).first()
        if vendedor_rol:
            vendedor_rol.permisos.set(maestro_vendedor.permisos.all())
            print("  - Permisos de Vendedor actualizados.")
            
        # Cliente
        cliente_rol = Rol.objects.filter(nombre__iexact='cliente', tenant=tenant).first()
        if cliente_rol:
            cliente_rol.permisos.set(maestro_cliente.permisos.all())
            print("  - Permisos de Cliente actualizados.")

print("\n¡Reparación completada con éxito!")
