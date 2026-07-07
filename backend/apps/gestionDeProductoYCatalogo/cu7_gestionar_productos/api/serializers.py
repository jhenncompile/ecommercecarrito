from rest_framework import serializers
from ..models import Producto
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.api.categoria_serializer import CategoriaSerializer
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.services.producto_service import ProductoService


class ProductoSerializer(serializers.ModelSerializer):
    categoria_detail = CategoriaSerializer(source='categoria', read_only=True)
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all()
    )

    # Precios calculados en el backend (evita duplicar la lógica en web/móvil)
    precio_original = serializers.SerializerMethodField()
    precio_final = serializers.SerializerMethodField()
    en_preventa = serializers.SerializerMethodField()

    # Reseñas y Calificaciones (CU-27): resumen para mostrar estrellas
    calificacion_promedio = serializers.SerializerMethodField()
    total_resenas = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'sku', 'descripcion', 'precio', 'costo',
            'stock', 'categoria', 'categoria_detail', 'atributos',
            'activo', 'imagen_url', 'creado_en', 'actualizado_en',
            'is_preorder', 'estimated_arrival_date', 'preorder_discount_percentage',
            'precio_original', 'precio_final', 'en_preventa',
            'calificacion_promedio', 'total_resenas',
        ]
        read_only_fields = [
            'id', 'creado_en', 'actualizado_en', 'categoria_detail',
            'precio_original', 'precio_final', 'en_preventa',
            'calificacion_promedio', 'total_resenas',
        ]

    def _pricing(self, obj):
        # Cachea el cálculo por instancia para no recalcular en cada campo
        if not hasattr(obj, '_pricing_cache'):
            obj._pricing_cache = ProductoService.calcular_precio(obj)
        return obj._pricing_cache

    def get_precio_original(self, obj):
        return self._pricing(obj)['precio_original']

    def get_precio_final(self, obj):
        return self._pricing(obj)['precio_final']

    def get_en_preventa(self, obj):
        return self._pricing(obj)['en_preventa']

    def _resumen_resenas(self, obj):
        # Cachea el resumen por instancia. Las reseñas viven en el schema del
        # tenant, así que en el schema público se devuelve vacío.
        if hasattr(obj, '_resenas_cache'):
            return obj._resenas_cache
        resumen = {'promedio': 0, 'total': 0}
        from django.db import connection
        if connection.schema_name != 'public':
            try:
                from apps.gestionDeClientes.cu26_gestionar_resenas.services.resena_service import ResenaService
                resumen = ResenaService().resumen_producto(obj.id)
            except Exception:
                resumen = {'promedio': 0, 'total': 0}
        obj._resenas_cache = resumen
        return resumen

    def get_calificacion_promedio(self, obj):
        return self._resumen_resenas(obj)['promedio']

    def get_total_resenas(self, obj):
        return self._resumen_resenas(obj)['total']

    def validate_sku(self, value):
        # Convertir string vacío a None para las actualizaciones.
        # En la creación, si viene vacío, se generará uno automáticamente en create().
        if value == "":
            return None
        return value

    def create(self, validated_data):
        sku = validated_data.get('sku')
        if not sku:
            from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
            # Obtener todos los SKUs actuales que sean numéricos
            skus_existentes = Producto.objects.exclude(sku__isnull=True).exclude(sku="").values_list('sku', flat=True)
            skus_numericos = set()
            for s in skus_existentes:
                if s.isdigit():
                    skus_numericos.add(int(s))
            
            # Buscar el primer "hueco" disponible empezando desde 1
            next_sku = 1
            while next_sku in skus_numericos:
                next_sku += 1
                
            validated_data['sku'] = str(next_sku)
            
        return super().create(validated_data)