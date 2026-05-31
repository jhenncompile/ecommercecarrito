import os
import sys
import django
from pathlib import Path

# Configurar Django
PROJECT_ROOT = Path(__file__).resolve().parent.parent / 'backend'
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.customers.models import Client
from apps.customers.users.models.usuario import Usuario
from apps.customers.users.models.rol import Rol
from django_tenants.utils import schema_context

def debug_permissions():
    print("--- DEBUGGING TENANTS & ROLES ---")
    for t in Client.objects.all():
        print(f"\nTenant: {t.schema_name} (Plan: {t.plan.nombre if t.plan else 'None'})")
        with schema_context(t.schema_name):
            # Usuarios
            for u in Usuario.objects.filter(tenant=t):
                print(f"  Usuario: {u.email}")
                print(f"    Roles: {[r.nombre for r in u.roles.all()]}")
                permisos = u.roles.filter(activo=True, permisos__activo=True).values_list('permisos__codigo', flat=True).distinct()
                print(f"    Permisos efectivos en roles: {list(permisos)}")
            
            # Roles locales
            for r in Rol.objects.filter(tenant=t):
                print(f"  Rol: {r.nombre} (Nivel: {r.nivel})")
                print(f"    Permisos asignados: {[p.codigo for p in r.permisos.all()]}")

if __name__ == '__main__':
    debug_permissions()
