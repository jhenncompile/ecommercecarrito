from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.authentication import ClienteJWTAuthentication, UsuarioJWTAuthentication
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.api.serializers import PedidoSerializer

class HistorialComprasViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de solo lectura enfocado en el cliente final.
    Devuelve Unicamente los pedidos (historial) del cliente autenticado.
    """
    serializer_class = PedidoSerializer
    authentication_classes = [ClienteJWTAuthentication, UsuarioJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from django.db import connection
        if connection.schema_name == 'public':
            return Pedido.objects.none()
            
        auth = getattr(self.request, 'auth', None)
        if hasattr(auth, 'get') and auth.get('role') == 'CLIENTE':
            cliente_id = auth.get('cliente_id') or auth.get('user_id')
            if cliente_id:
                # Retornar los pedidos cuyo carrito estÃ¡ asociado a este cliente
                return Pedido.objects.filter(carrito__cliente_id=cliente_id).order_by('-fecha_pedido')
        
        # Si es un usuario admin o sin cliente_id, no se devuelve el historial pÃºblico,
        # (o podrÃ­amos retornar none, o todos, pero lo mejor es restringirlo a su ID).
        return Pedido.objects.none()
