from rest_framework import serializers
from ..models.plan import Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'nombre', 'descripcion', 'precio_mensual', 
            'precio_anual', 'max_usuarios', 'max_productos', 
            'facturacion_max', 'activo'
        ]
        read_only_fields = ['id']
