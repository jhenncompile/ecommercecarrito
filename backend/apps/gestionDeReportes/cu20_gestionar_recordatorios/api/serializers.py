# apps/negocio/recordatorios/api/serializers.py
from rest_framework import serializers
from apps.gestionDeReportes.cu20_gestionar_recordatorios.models.recordatorio import Recordatorio


class RecordatorioSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    pedido_numero = serializers.SerializerMethodField()
    esta_vencido = serializers.SerializerMethodField()

    class Meta:
        model = Recordatorio
        fields = [
            'id',
            'titulo',
            'descripcion',
            'tipo',
            'tipo_display',
            'fecha_recordatorio',
            'completado',
            'pedido',
            'pedido_numero',
            'notificacion_enviada',
            'fecha_creacion',
            'fecha_actualizacion',
            'esta_vencido',
        ]
        read_only_fields = ['id', 'usuario', 'notificacion_enviada', 'fecha_creacion', 'fecha_actualizacion']

    def get_pedido_numero(self, obj):
        if obj.pedido:
            return obj.pedido.id
        return None

    def get_esta_vencido(self, obj):
        from django.utils import timezone
        return not obj.completado and obj.fecha_recordatorio < timezone.now()

    def validate_fecha_recordatorio(self, value):
        """Validar que la fecha sea válida (puede ser futura o pasada para recordatorios históricos)."""
        return value
