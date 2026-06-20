from rest_framework.response import Response
from rest_framework import status
from apps.core.views import BaseViewSet
from apps.customers.models import Rol
from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.api.rol_serializer import RolSerializer
from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.services.rol_service import RolService


class RolViewSet(BaseViewSet):
    """
    API de Roles.
    
    - GET /api/roles/ - Listar todos
    - POST /api/roles/ - Crear nuevo
    - GET /api/roles/{id}/ - Detalle
    - PUT /api/roles/{id}/ - Actualizar
    - DELETE /api/roles/{id}/ - Eliminar
    """
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    modulo_auditoria = "Rol"
    
    def get_queryset(self):
        from django.db import connection
        from django.db.models import Q
        qs = super().get_queryset()
        if connection.schema_name != 'public':
            # Mostrar roles globales (tenant=None) Y los específicos de la tienda
            return qs.filter(Q(tenant__schema_name=connection.schema_name) | Q(tenant__isnull=True))
        return qs

    def perform_create(self, serializer):
        from django.db import connection
        from apps.customers.models import Client
        
        # Asignación automática de tenant si estamos en una tienda
        if connection.schema_name != 'public':
            tenant = Client.objects.get(schema_name=connection.schema_name)
            serializer.save(tenant=tenant)
        else:
            serializer.save()

    def get_service(self):
        return RolService()
