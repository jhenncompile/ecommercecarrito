from django.db.models import Count, Max
from apps.core.services import BaseService
from apps.gestionDeClientes.cu25_gestionar_solicitud_de_restock.models.restock_request import RestockRequest
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto


class RestockService(BaseService):
    """Servicio de Solicitudes de Restock (CU-25)."""

    def __init__(self):
        super().__init__(RestockRequest)

    def registrar_solicitud(self, cliente_id, producto_id):
        """
        Registra la intención de compra de un cliente sobre un producto.
        Evita duplicados para el mismo cliente y producto (get_or_create).
        Devuelve (instancia, creado).
        """
        return RestockRequest.objects.get_or_create(
            cliente_id=cliente_id,
            producto_id=producto_id,
            defaults={'status': 'pending'},
        )

    def ranking_mas_solicitados(self):
        """
        Ranking de productos más solicitados usando el ORM (annotate + Count).
        Ordena por mayor cantidad de solicitudes e incluye la fecha de la
        última solicitud.
        """
        return (
            Producto.objects
            .annotate(
                total_solicitudes=Count('restock_requests'),
                ultima_solicitud=Max('restock_requests__created_at'),
            )
            .filter(total_solicitudes__gt=0)
            .order_by('-total_solicitudes', 'nombre')
        )
