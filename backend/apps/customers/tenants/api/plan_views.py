from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.core.views import BaseViewSet
from apps.customers.models import Plan
from apps.customers.tenants.api.serializers import PlanSerializer
from apps.customers.tenants.services.plan_service import PlanService


class PlanViewSet(BaseViewSet):
    """
    API de Planes de Suscripción.
    
    - GET /api/planes/ - Listar todos
    - POST /api/planes/ - Crear nuevo
    - GET /api/planes/{id}/ - Detalle
    - PUT /api/planes/{id}/ - Actualizar
    - DELETE /api/planes/{id}/ - Eliminar
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    modulo_auditoria = "Plan"
    pagination_class = None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = PlanService()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """Devuelve el catálogo canónico (sin planes duplicados por nombre)."""
        from rest_framework.response import Response
        planes = self.service.obtener_planes_canonicos()
        serializer = self.get_serializer(planes, many=True)
        return Response(serializer.data)
