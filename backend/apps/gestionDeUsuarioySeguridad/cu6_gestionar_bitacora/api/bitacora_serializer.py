from rest_framework import serializers
from apps.gestionDeUsuarioySeguridad.cu6_gestionar_bitacora.models.bitacora import Bitacora

class BitacoraSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='idUsuario.first_name', read_only=True)
    usuario_email = serializers.CharField(source='idUsuario.email', read_only=True)

    class Meta:
        model = Bitacora
        fields = ['id', 'idUsuario', 'usuario_nombre', 'usuario_email', 'fecha', 'accion', 'modulo', 'metadatos']
