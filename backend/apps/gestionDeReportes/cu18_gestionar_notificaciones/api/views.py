from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.gestionDeReportes.cu18_gestionar_notificaciones.models.notificacion import Notificacion
from apps.gestionDeReportes.cu18_gestionar_notificaciones.api.serializers import NotificacionSerializer
from apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.authentication import ClienteJWTAuthentication

class NotificacionViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from django.db import connection
        from apps.customers.clientes.models.cliente import Cliente
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return Notificacion.objects.none()
            
        email = getattr(user, 'email', None) or getattr(user, 'correo', None)
        if not email:
            return Notificacion.objects.none()
            
        if connection.schema_name == 'public':
            return Notificacion.objects.none()
            
        try:
            # Intentar buscar como cliente primero
            cliente = Cliente.objects.get(correo=email)
            return Notificacion.objects.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            # Si no es cliente, buscar como usuario (vendedor)
            return Notificacion.objects.filter(usuario=user)

    @action(detail=False, methods=['post'], url_path='marcar-todas-leidas')
    def marcar_todas_leidas(self, request):
        queryset = self.get_queryset()
        queryset.filter(leido=False).update(leido=True)
        return Response({'status': 'Todas las notificaciones marcadas como leÃ­das'})

