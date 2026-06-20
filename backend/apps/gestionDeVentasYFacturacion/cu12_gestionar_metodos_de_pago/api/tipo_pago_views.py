from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.models.tipo_pago import TipoPago
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.api.tipo_pago_serializer import TipoPagoSerializer

class TipoPagoViewSet(viewsets.ModelViewSet):
    queryset = TipoPago.objects.all()
    serializer_class = TipoPagoSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['nombre']
    ordering_fields = ['nombre']
