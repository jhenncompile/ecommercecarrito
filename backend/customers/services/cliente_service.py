from core.services import BaseService
from ..models.cliente import Cliente
from django.contrib.auth.hashers import make_password


class ClienteService(BaseService):
    """Servicio de Clientes (Customers)."""
    
    def __init__(self):
        super().__init__(Cliente)
    
    def crear_cliente_con_contrasena(self, datos):
        """Crea un cliente encriptando la contraseña."""
        if 'contrasena' in datos:
            datos['contrasena'] = make_password(datos['contrasena'])
        return self.crear(datos)
    
    def obtener_por_correo(self, correo):
        """Obtiene un cliente por correo."""
        return Cliente.objects.filter(correo=correo).first()
    
    def obtener_activos(self):
        """Obtiene solo clientes activos."""
        return Cliente.objects.filter(activo=True)
    
    def activar(self, cliente_id):
        """Activa un cliente."""
        cliente = self.obtener(cliente_id)
        cliente.activo = True
        cliente.save()
        return cliente
    
    def desactivar(self, cliente_id):
        """Desactiva un cliente."""
        cliente = self.obtener(cliente_id)
        cliente.activo = False
        cliente.save()
        return cliente
