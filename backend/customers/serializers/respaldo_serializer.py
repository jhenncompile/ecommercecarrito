from rest_framework import serializers
from ..models.respaldo import RespaldoSistema

class RespaldoSerializer(serializers.ModelSerializer):
    fecha_display = serializers.SerializerMethodField()
    anterior_id = serializers.PrimaryKeyRelatedField(source='anterior', read_only=True)
    siguiente_id = serializers.PrimaryKeyRelatedField(source='siguiente', read_only=True)
    
    class Meta:
        model = RespaldoSistema
        fields = [
            'id', 'nombre', 'timestamp', 'fecha_display', 
            'archivo_path', 'anterior_id', 'siguiente_id', 'metadata'
        ]

    def get_fecha_display(self, obj):
        from django.utils import timezone
        import pytz
        tz_bo = pytz.timezone('America/La_Paz')
        dt = obj.timestamp
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.utc)
            
        local_dt = dt.astimezone(tz_bo)
        return local_dt.strftime('%d/%m %H:%M')
