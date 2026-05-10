from core.services import BaseService
from ..models.plan import Plan


class PlanService(BaseService):
    """Servicio de Planes de Suscripción."""
    
    def __init__(self):
        super().__init__(Plan)
    
    def obtener_activos(self):
        """Obtiene solo los planes activos."""
        return Plan.objects.filter(activo=True)
    
    def obtener_por_nombre(self, nombre):
        """Obtiene un plan por nombre."""
        return Plan.objects.filter(nombre=nombre).first()
