from rest_framework.decorators import action
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Case, When
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.api.serializers import ProductoSerializer
from apps.gestionDeProductoYCatalogo.cu23_gestionar_filtro_de_producto.api.filters import ProductoAtributosFilterBackend

class CatalogoProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint pÃºblico optimizado para el front-end del e-commerce.
    Solo permite lectura y filtra Ãºnicamente los productos activos.
    """
    serializer_class = ProductoSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter, 
        ProductoAtributosFilterBackend
    ]
    filterset_fields = {
        'precio': ['gte', 'lte'],
        'categoria': ['exact'],
        'sku': ['exact'],
    }
    search_fields = ['nombre', 'descripcion', 'sku']
    ordering_fields = ['precio', 'creado_en', 'nombre', 'stock']
    ordering = ['-creado_en']
    
    def get_queryset(self):
        from django.db import connection
        if connection.schema_name == 'public':
            return Producto.objects.none()
        
        # El catÃ¡logo pÃºblico solo muestra productos activos
        return Producto.objects.filter(activo=True)

    @action(detail=True, methods=['get'], url_path='recomendaciones')
    def recomendaciones(self, request, pk=None):
        from rest_framework.response import Response
        from rest_framework import status
        from apps.gestionDeClientes.cu16_recomendar_productos.services.recommendation_service import RecommendationService
        from apps.gestionDeClientes.cu16_recomendar_productos.api.recommendation_serializer import ProductoRecomendadoSerializer
        
        try:
            p_id = int(pk)
        except (ValueError, TypeError):
            return Response({"error": "ID invÃ¡lido"}, status=status.HTTP_400_BAD_REQUEST)

        service = RecommendationService()
        reco_data = service.obtener_recomendaciones(p_id)
        
        if not reco_data:
            return Response([])

        reco_ids = [item[0] for item in reco_data]
        scores_map = {item[0]: item[1] for item in reco_data}

        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(reco_ids)])
        productos = Producto.objects.filter(id__in=reco_ids, activo=True).order_by(preserved_order)

        for p in productos:
            p.score = scores_map.get(p.id, 0.0)

        serializer = ProductoRecomendadoSerializer(productos, many=True)
        return Response({
            "product_id": p_id,
            "recommendations": serializer.data,
            "meta": {"count": len(serializer.data), "engine": "tfidf_cosine_v2"}
        })
