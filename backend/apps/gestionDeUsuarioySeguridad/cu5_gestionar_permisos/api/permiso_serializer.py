from rest_framework import serializers
from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.models.permiso import Permiso

class PermisoSerializer(serializers.ModelSerializer):
    roles_asociados = serializers.SerializerMethodField()

    def get_roles_asociados(self, obj):
        return [{'id': r.id, 'nombre': r.nombre} for r in obj.roles.all()]

    class Meta:
        model = Permiso
        fields = '__all__'
        read_only_fields = ['id']
