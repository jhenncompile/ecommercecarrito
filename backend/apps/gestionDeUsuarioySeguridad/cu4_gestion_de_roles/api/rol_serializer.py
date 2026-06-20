from rest_framework import serializers
from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.models.rol import Rol


from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.api.permiso_serializer import PermisoSerializer

class RolSerializer(serializers.ModelSerializer):
    permisos_detalles = PermisoSerializer(source='permisos', many=True, read_only=True)
    is_global = serializers.SerializerMethodField()
    
    def get_is_global(self, obj):
        return obj.tenant is None
    
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'nivel', 'permisos', 'permisos_detalles', 'activo', 'tenant', 'is_global']
        read_only_fields = ['id', 'permisos_detalles', 'is_global']
