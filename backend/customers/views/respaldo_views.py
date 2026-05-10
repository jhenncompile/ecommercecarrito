from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from ..models.respaldo import RespaldoSistema
from ..serializers.respaldo_serializer import RespaldoSerializer
from ..services.respaldo_service import RespaldoService

class RespaldoViewSet(viewsets.ModelViewSet):
    """
    API para gestión de Respaldos con Versionado Encadenado.
    """
    queryset = RespaldoSistema.objects.all()
    serializer_class = RespaldoSerializer
    permission_classes = [IsAdminUser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = RespaldoService()

    def create(self, request, *args, **kwargs):
        """Sobrescribe el POST para ejecutar la creación real del backup"""
        nombre = request.data.get('nombre', 'Respaldo Manual')
        try:
            respaldo = self.service.crear_respaldo(nombre)
            serializer = self.get_serializer(respaldo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='historial')
    def historial_encadenado(self, request):
        """Retorna el historial con la lógica de cola y siguiente"""
        respaldos = self.service.obtener_historial_encadenado()
        serializer = self.get_serializer(respaldos, many=True)
        return Response(serializer.data)
