from rest_framework import serializers
from ..models.rol import Rol


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'nivel', 'activo']
        read_only_fields = ['id']
