import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from apps.negocio.models import Pedido

def revert(schema, pid, estado):
    with schema_context(schema):
        try:
            p = Pedido.objects.get(id=pid)
            p.estado = estado
            p.save()
            print(f"Reverted {schema} {pid} to {estado}")
        except Exception as e:
            print(e)

revert('tecno', 33, 'PROCESADO')
revert('hogar', 84, 'PROCESADO')
revert('sony', 193, 'ENVIADO')
