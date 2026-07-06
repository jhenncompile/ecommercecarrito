from django.db import connection
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.customers.clientes.models.cliente import Cliente
from apps.gestionDeClientes.cu25_gestionar_solicitud_de_restock.api.serializers import (
    RestockRequestSerializer, RestockRankingSerializer
)
from apps.gestionDeClientes.cu25_gestionar_solicitud_de_restock.services.restock_service import RestockService


class RestockRequestViewSet(viewsets.ViewSet):
    """
    API de Solicitudes de Restock (CU-25 Intención de Compra).

    - POST /api/restock/          - Registrar solicitud (cliente autenticado)
    - GET  /api/restock/ranking/  - Ranking de productos más solicitados
    """
    permission_classes = [IsAuthenticated]

    def get_service(self):
        return RestockService()

    def create(self, request):
        """Registra la intención de compra del cliente sobre un producto agotado."""
        if connection.schema_name == 'public':
            return Response({'error': 'Operación no disponible en el esquema público.'}, status=status.HTTP_400_BAD_REQUEST)

        producto_id = request.data.get('producto_id') or request.data.get('producto')
        if not producto_id:
            return Response({'error': 'producto_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el cliente desde el token JWT de cliente (mismo patrón que Pedido)
        email = getattr(request.user, 'email', getattr(request.user, 'correo', None))
        if not email:
            return Response({'error': 'Debes iniciar sesión como cliente.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            cliente = Cliente.objects.get(correo=email)
        except Cliente.DoesNotExist:
            return Response({'error': 'Cliente no encontrado.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            solicitud, creado = self.get_service().registrar_solicitud(cliente.id, producto_id)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RestockRequestSerializer(solicitud)
        mensaje = 'Te avisaremos cuando el producto vuelva a estar disponible.' if creado \
            else 'Ya tenías una solicitud registrada para este producto.'
        return Response(
            {'creado': creado, 'mensaje': mensaje, 'solicitud': serializer.data},
            status=status.HTTP_201_CREATED if creado else status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def ranking(self, request):
        """Ranking de productos más solicitados (para el dashboard del vendedor)."""
        if connection.schema_name == 'public':
            return Response([])
        queryset = self.get_service().ranking_mas_solicitados()
        serializer = RestockRankingSerializer(queryset, many=True)
        return Response(serializer.data)
