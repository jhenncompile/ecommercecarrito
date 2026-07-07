from django.db import connection
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.customers.clientes.models.cliente import Cliente
from apps.gestionDeClientes.cu26_gestionar_resenas.api.serializers import ResenaSerializer
from apps.gestionDeClientes.cu26_gestionar_resenas.services.resena_service import ResenaService


class ResenaViewSet(viewsets.ViewSet):
    """
    API de Reseñas y Calificaciones (CU-27).

    - POST /api/resenas/                     - Crear/actualizar reseña (cliente autenticado y comprador verificado)
    - GET  /api/resenas/producto/<id>/       - Reseñas + resumen de un producto (público)
    - GET  /api/resenas/                     - Todas las reseñas de la tienda (vendedor)
    """

    def get_permissions(self):
        if self.action in ['por_producto', 'list']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_service(self):
        return ResenaService()

    def _cliente_actual(self, request):
        """Obtiene el Cliente autenticado desde el token JWT de cliente."""
        email = getattr(request.user, 'email', getattr(request.user, 'correo', None))
        if not email:
            return None
        return Cliente.objects.filter(correo=email).first()

    def create(self, request):
        """Registra o actualiza la reseña de un producto (solo compradores verificados)."""
        if connection.schema_name == 'public':
            return Response({'error': 'Operación no disponible en el esquema público.'}, status=status.HTTP_400_BAD_REQUEST)

        producto_id = request.data.get('producto_id') or request.data.get('producto')
        calificacion = request.data.get('calificacion')
        comentario = request.data.get('comentario', '')

        if not producto_id:
            return Response({'error': 'producto_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        cliente = self._cliente_actual(request)
        if not cliente:
            return Response({'error': 'Debes iniciar sesión como cliente.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            resena, creada = self.get_service().crear_o_actualizar(
                cliente.id, producto_id, calificacion, comentario
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResenaSerializer(resena)
        return Response(
            {'creada': creada, 'resena': serializer.data},
            status=status.HTTP_201_CREATED if creada else status.HTTP_200_OK
        )

    def list(self, request):
        """Todas las reseñas de la tienda (para el vendedor)."""
        if connection.schema_name == 'public':
            return Response([])
        from apps.gestionDeClientes.cu26_gestionar_resenas.models.resena import Resena
        qs = Resena.objects.select_related('cliente', 'producto').order_by('-created_at')
        data = [
            {
                **ResenaSerializer(r).data,
                'producto_nombre': r.producto.nombre,
            }
            for r in qs
        ]
        return Response(data)

    @action(detail=False, methods=['get'], url_path='producto/(?P<producto_id>[^/.]+)')
    def por_producto(self, request, producto_id=None):
        """Resumen + lista de reseñas de un producto. Incluye la reseña propia y
        si el cliente autenticado puede reseñar (comprador verificado)."""
        if connection.schema_name == 'public':
            return Response({'resumen': {'promedio': 0, 'total': 0}, 'resenas': [], 'mi_resena': None, 'puede_resenar': False})

        service = self.get_service()
        resenas = ResenaSerializer(service.resenas_de_producto(producto_id), many=True).data
        resumen = service.resumen_producto(producto_id)

        mi_resena = None
        puede_resenar = False
        cliente = self._cliente_actual(request) if request.user and request.user.is_authenticated else None
        if cliente:
            existente = service.mi_resena(cliente.id, producto_id)
            mi_resena = ResenaSerializer(existente).data if existente else None
            puede_resenar = service.cliente_compro_producto(cliente.id, producto_id)

        return Response({
            'resumen': resumen,
            'resenas': resenas,
            'mi_resena': mi_resena,
            'puede_resenar': puede_resenar,
        })
