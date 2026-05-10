from core.views import BaseViewSet
from customers.models import Permiso
from customers.serializers.permiso_serializer import PermisoSerializer

class PermisoViewSet(BaseViewSet):
    """
    API de Permisos.
    
    - GET /api/permisos/ - Listar todos
    - POST /api/permisos/ - Crear nuevo
    - GET /api/permisos/{id}/ - Detalle
    - PUT /api/permisos/{id}/ - Actualizar
    - DELETE /api/permisos/{id}/ - Eliminar
    """
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    modulo_auditoria = "Permiso"
    search_fields = ['nombre', 'codigo', 'modulo']
    filterset_fields = ['modulo', 'activo']
