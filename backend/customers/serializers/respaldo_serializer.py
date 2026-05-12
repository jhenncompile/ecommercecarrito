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
        return obj.timestamp.strftime('%d/%m %H:%M')
