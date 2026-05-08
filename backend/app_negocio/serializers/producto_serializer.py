from rest_framework import serializers
from ..models import Producto
from ..models.categoria import Categoria
from .categoria_serializer import CategoriaSerializer


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