# backend/app_negocio/serializers/recommendation_serializer.py
from rest_framework import serializers
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto

class ProductoRecomendadoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    # Añadimos el score de IA para que el móvil pueda decidir si mostrarlo o no
    score = serializers.FloatField(read_only=True, default=0.0)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'precio', 'imagen_url', 
            'categoria_nombre', 'stock', 'score'
        ]