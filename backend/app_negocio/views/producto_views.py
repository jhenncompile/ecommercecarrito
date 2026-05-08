from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from core.views import BaseViewSet
from ..models.producto import Producto
from ..serializers.producto_serializer import ProductoSerializer

class ProductoViewSet(BaseViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    modulo_auditoria = "Producto"
    
    # Filtros y Búsqueda
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'precio': ['gte', 'lte'],
        'categoria': ['exact'],
        'activo': ['exact'],
        'sku': ['exact'],
    }
    search_fields = ['nombre', 'descripcion', 'sku']
    ordering_fields = ['precio', 'creado_en', 'nombre', 'stock']
    ordering = ['-creado_en']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro dinámico por atributos JSON
        # Uso: ?attr_color=rojo&attr_talla=M
        params = self.request.query_params
        attr_filters = {
            f"atributos__{key[5:]}__icontains": value 
            for key, value in params.items() 
            if key.startswith('attr_')
        }
        
        if attr_filters:
            queryset = queryset.filter(**attr_filters)
            
        return queryset

    def get_permissions(self):
        """
        Permite lectura pública (AllowAny para GET)
        Pero requiere autenticación para crear/editar/eliminar
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]