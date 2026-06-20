from apps.core.services import BaseService
from ..models.rol import Rol


class RolService(BaseService):
    """Servicio de Roles."""
    
    def __init__(self):
        super().__init__(Rol)
    
    def obtener_por_nombre(self, nombre):
        """Obtiene un rol por nombre."""
        return Rol.objects.filter(nombre=nombre).first()
    
    def obtener_por_nivel(self, nivel):
        """Obtiene roles por nivel de permiso."""
        return Rol.objects.filter(nivel=nivel)
