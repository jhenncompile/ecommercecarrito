from rest_framework import serializers
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.models.tipo_pago import TipoPago

class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPago
        fields = '__all__'
