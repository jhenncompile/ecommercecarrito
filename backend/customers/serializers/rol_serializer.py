from rest_framework import serializers
from ..models.rol import Rol


from .permiso_serializer import PermisoSerializer

class RolSerializer(serializers.ModelSerializer):
    permisos_detalles = PermisoSerializer(source='permisos', many=True, read_only=True)
    
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'nivel', 'permisos', 'permisos_detalles', 'activo']
        read_only_fields = ['id', 'permisos_detalles']
