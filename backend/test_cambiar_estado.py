import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from apps.customers.models import Client
from apps.negocio.models import Pedido
from apps.negocio.ordenes.services.pedido_service import PedidoService
from apps.negocio.ordenes.api.pedido_serializer import PedidoSerializer

tenants = Client.objects.exclude(schema_name='public')
for t in tenants:
    with schema_context(t.schema_name):
        try:
            p = Pedido.objects.last()
            if p:
                print(f"[{t.schema_name}] Pedido: {p.id}")
                try:
                    p = PedidoService().cambiar_estado(p.id, 'ENTREGADO')
                    ser = PedidoSerializer(p)
                    data = ser.data
                    print(f"[{t.schema_name}] Serializer exitoso")
                except Exception as e:
                    import traceback
                    print(f"[{t.schema_name}] Error: {e}")
                    traceback.print_exc()
        except Exception as e:
            pass
