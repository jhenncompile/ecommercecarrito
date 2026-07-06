from apps.core.services import BaseService
from apps.gestionDeVentasYFacturacion.cu24_gestionar_logistica.models.delivery_zone import DeliveryZone


class DeliveryZoneService(BaseService):
    """Servicio de Zonas de Delivery (CU-24)."""

    def __init__(self):
        super().__init__(DeliveryZone)

    def obtener_activas(self):
        """Devuelve solo las zonas activas del tenant actual."""
        return DeliveryZone.objects.filter(activo=True)
