from rest_framework import serializers
from ..models import Producto
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.api.categoria_serializer import CategoriaSerializer


class ProductoSerializer(serializers.ModelSerializer):
    categoria_detail = CategoriaSerializer(source='categoria', read_only=True)
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all()
    )

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'sku', 'descripcion', 'precio', 'costo',
            'stock', 'categoria', 'categoria_detail', 'atributos',
            'activo', 'imagen_url', 'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en', 'categoria_detail']

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