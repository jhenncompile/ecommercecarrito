from rest_framework import serializers
from apps.gestionDeVentasYFacturacion.cu24_gestionar_logistica.models.delivery_zone import DeliveryZone


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = ['id', 'zone_name', 'price', 'activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']
