from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from apps.core.views import BaseViewSet
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Case, When
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.api.serializers import ProductoSerializer


class ProductoViewSet(BaseViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    modulo_auditoria = "Producto"
    
    # Filtros y BÃºsqueda
    from apps.gestionDeProductoYCatalogo.cu23_gestionar_filtro_de_producto.api.filters import ProductoAtributosFilterBackend
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, ProductoAtributosFilterBackend]
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
        from django.db import connection
        if connection.schema_name == 'public':
            return Producto.objects.none()
        return super().get_queryset()

    def get_permissions(self):
        """
        Permite lectura pública (AllowAny para GET)
        Pero requiere autenticación para crear/editar/eliminar
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        from django.db import connection
        schema_name = connection.schema_name
        
        if schema_name != 'public':
            from apps.customers.tenants.models.tenant import Client
            try:
                tenant = Client.objects.get(schema_name=schema_name)
                if tenant.plan:
                    max_productos = tenant.plan.max_productos
                    # max_productos == 0 puede significar "ilimitado", validamos si es mayor a 0
                    if max_productos > 0:
                        current_count = Producto.objects.count()
                        if current_count >= max_productos:
                            from rest_framework.exceptions import ValidationError
                            raise ValidationError({"limite_alcanzado": f"Tu plan ({tenant.plan.nombre}) permite un máximo de {max_productos} productos. Mejora tu plan para añadir más."})
            except Client.DoesNotExist:
                pass
                
        super().perform_create(serializer)
    
