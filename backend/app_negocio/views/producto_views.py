from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from core.views import BaseViewSet
from ..models.producto import Producto
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Case, When
from ..serializers.producto_serializer import ProductoSerializer
from ..serializers.recommendation_serializer import ProductoRecomendadoSerializer


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
    
    @action(detail=True, methods=['get'], url_path='recomendaciones')
    def recomendaciones(self, request, pk=None):
        from ..services.recommendation_service import RecommendationService
        
        # Validación de entrada (Evita el Error 500)
        try:
            p_id = int(pk)
        except (ValueError, TypeError):
            return Response({"error": "ID inválido"}, status=status.HTTP_400_BAD_REQUEST)

        service = RecommendationService()
        reco_data = service.obtener_recomendaciones(p_id) # Retorna [(id, score), ...]
        
        if not reco_data:
            return Response([])

        reco_ids = [item[0] for item in reco_data]
        scores_map = {item[0]: item[1] for item in reco_data}

        # Preservar el orden de relevancia de la IA en la Query
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(reco_ids)])
        
        productos = Producto.objects.filter(id__in=reco_ids, activo=True).order_by(preserved_order)

        # Inyectamos el score manualmente antes de serializar
        for p in productos:
            p.score = scores_map.get(p.id, 0.0)

        serializer = ProductoRecomendadoSerializer(productos, many=True)
        
        return Response({
            "product_id": p_id,
            "recommendations": serializer.data,
            "meta": {"count": len(serializer.data), "engine": "tfidf_cosine_v2"}
        })