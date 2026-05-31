from rest_framework import serializers
from apps.negocio.reportes.models.reporte_config import ReporteConfig

class ReporteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteConfig
        fields = '__all__'


class ForecastRequestSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(
        choices=['ventas_cantidad', 'ventas_totales', 'por_producto', 'por_categoria'],
        default='ventas_cantidad',
        required=False,
    )
    granularidad = serializers.CharField(default='mes', required=False)
    data_historica_meses = serializers.IntegerField(min_value=3, max_value=1200, default=12, required=False)
    prediccion_meses = serializers.IntegerField(min_value=1, max_value=120, default=3, required=False)
    producto_id = serializers.IntegerField(required=False, allow_null=True)
    categoria_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        tipo = attrs.get('tipo', 'ventas_cantidad')
        if tipo == 'por_producto' and not attrs.get('producto_id'):
            raise serializers.ValidationError({'producto_id': 'Este campo es requerido para predicción por producto.'})
        if tipo == 'por_categoria' and not attrs.get('categoria_id'):
            raise serializers.ValidationError({'categoria_id': 'Este campo es requerido para predicción por categoría.'})
        return attrs
