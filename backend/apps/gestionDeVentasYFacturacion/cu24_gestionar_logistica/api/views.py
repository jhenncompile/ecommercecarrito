from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.core.views import BaseViewSet
from apps.gestionDeVentasYFacturacion.cu24_gestionar_logistica.models.delivery_zone import DeliveryZone
from apps.gestionDeVentasYFacturacion.cu24_gestionar_logistica.api.serializers import DeliveryZoneSerializer
from apps.gestionDeVentasYFacturacion.cu24_gestionar_logistica.services.delivery_zone_service import DeliveryZoneService


class DeliveryZoneViewSet(BaseViewSet):
    """
    API de Zonas de Delivery (CU-24). Gestión para el vendedor.

    - GET    /api/zonas-delivery/       - Listar zonas del tenant
    - POST   /api/zonas-delivery/       - Crear zona
    - GET    /api/zonas-delivery/{id}/  - Detalle
    - PUT    /api/zonas-delivery/{id}/  - Actualizar
    - DELETE /api/zonas-delivery/{id}/  - Eliminar
    """
    queryset = DeliveryZone.objects.all()
    serializer_class = DeliveryZoneSerializer
    modulo_auditoria = "DeliveryZone"

    def get_queryset(self):
        if connection.schema_name == 'public':
            return DeliveryZone.objects.none()
        return super().get_queryset()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = DeliveryZoneService()


class ConfiguracionEnvioView(APIView):
    """
    Configuración de envíos que consume el storefront público durante el checkout.

    Devuelve la ciudad de la tienda, los flags de logística y las zonas de
    delivery activas para que el cliente calcule el costo de envío.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        if connection.schema_name == 'public':
            return Response({
                'ciudad': None,
                'whatsapp': None,
                'enable_local_delivery': False,
                'enable_national_shipping': True,
                'zonas': []
            })

        tenant = request.tenant
        zonas = DeliveryZoneSerializer(
            DeliveryZone.objects.filter(activo=True), many=True
        ).data

        return Response({
            'ciudad': getattr(tenant, 'ciudad', None),
            'whatsapp': getattr(tenant, 'whatsapp', None),
            'enable_local_delivery': getattr(tenant, 'enable_local_delivery', False),
            'enable_national_shipping': getattr(tenant, 'enable_national_shipping', True),
            'zonas': zonas
        })
