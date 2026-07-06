from rest_framework import serializers
from apps.gestionDeClientes.cu25_gestionar_solicitud_de_restock.models.restock_request import RestockRequest


class RestockRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestockRequest
        fields = ['id', 'cliente', 'producto', 'status', 'created_at']
        read_only_fields = ['id', 'cliente', 'status', 'created_at']


class RestockRankingSerializer(serializers.Serializer):
    """Ranking de productos más solicitados (Intención de Compra)."""
    producto_id = serializers.IntegerField(source='id')
    producto = serializers.CharField(source='nombre')
    stock = serializers.IntegerField()
    cantidad_solicitudes = serializers.IntegerField(source='total_solicitudes')
    ultima_solicitud = serializers.DateTimeField()
