from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from customers.models import Client
from customers.serializers.tenant_serializer import TiendaPublicSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser


class DirectorioPagination(PageNumberPagination):
    """
    Paginación personalizada para el directorio de tiendas.
    Muestra 12 tiendas por página para la grilla del frontend.
    """
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class TiendaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint público para listar y buscar tiendas en el Marketplace (Escenario C).
    
    Características:
    - Solo tiendas activas
    - Acceso público sin autenticación (AllowAny)
    - Optimización de consultas con prefetch_related
    - Paginación de 12 tiendas por página
    - Filtrado por categoría
    - Búsqueda de texto libre en nombre y descripción
    
    Endpoints:
    - GET /api/tiendas-publicas/ - Listar tiendas públicas (paginado)
    - GET /api/tiendas-publicas/?search=boutique - Buscar por texto
    - GET /api/tiendas-publicas/?categoria_tienda=ropa - Filtrar por categoría
    """
    
    # Solo tiendas activas
    queryset = Client.objects.filter(activo=True).prefetch_related('domains')
    serializer_class = TiendaPublicSerializer
    permission_classes = [AllowAny]  # Acceso sin JWT
    pagination_class = DirectorioPagination
    
    # Filtros y búsqueda
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['categoria_tienda']  # Permite filtrado exacto por categoría
    search_fields = ['nombre_comercial', 'descripcion']  # Búsqueda por texto libre


class TiendaPerfilView(APIView):
    """
    Endpoint para que el vendedor administre los datos de su propia tienda.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        tenant = request.tenant
        serializer = TiendaPublicSerializer(tenant)
        return Response(serializer.data)

    def patch(self, request):
        tenant = request.tenant
        
        # Manually parse the data to allow updating icono
        if 'nombre_comercial' in request.data:
            tenant.nombre_comercial = request.data['nombre_comercial']
        if 'descripcion' in request.data:
            tenant.descripcion = request.data['descripcion']
        if 'categoria_tienda' in request.data:
            tenant.categoria_tienda = request.data['categoria_tienda']
        if 'icono' in request.FILES:
            tenant.icono = request.FILES['icono']
            
        tenant.save()
        serializer = TiendaPublicSerializer(tenant)
        return Response(serializer.data, status=status.HTTP_200_OK)
