from django.db import connection
from rest_framework import viewsets
from .mixins import AuditoriaMixin

class BaseViewSet(AuditoriaMixin, viewsets.ModelViewSet):
    """
    BaseViewSet que proporciona auditoría automática y seguridad de esquemas.
    """
    
    def get_queryset(self):
        """
        Evita errores de 'table not found' si se accede a un modelo de tenant
        desde el esquema público.
        """
        # Si estamos en el esquema público, no deberíamos consultar modelos de negocio
        # (a menos que el modelo esté explícitamente en SHARED_APPS)
        if connection.schema_name == 'public':
            try:
                table_name = self.queryset.model._meta.db_table
                if table_name not in connection.introspection.table_names():
                    return self.queryset.none()
            except Exception:
                return self.queryset.none()
                
        return super().get_queryset()