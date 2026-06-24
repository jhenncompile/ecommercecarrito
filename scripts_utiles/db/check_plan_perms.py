import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.customers.tenants.models.tenant import Client
from apps.customers.tenants.models.plan import Plan
from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.models.permiso import Permiso
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.models.usuario import Usuario
from django_tenants.utils import schema_context

schema = 'shopcazarescalvilloe'
print(f"Checking tenant {schema}...")
tenant = Client.objects.get(schema_name=schema)
plan = tenant.plan
print(f"Plan: {plan.nombre} (ID: {plan.id})")
print(f"Plan Permissions:")
for p in plan.permisos.all():
    print(f" - {p.codigo}")

with schema_context(schema):
    vendedor = Usuario.objects.get(id=6)
    print(f"User 6 roles:")
    for r in vendedor.roles.all():
        print(f" - {r.nombre}")
        for p in r.permisos.all():
            print(f"   * {p.codigo}")
