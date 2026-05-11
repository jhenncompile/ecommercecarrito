from rest_framework import serializers
from app_negocio.models import Carrito, CarritoItem, Producto
from app_negocio.serializers.producto_serializer import ProductoSerializer
from customers.models import Cliente


class CarritoItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_precio = serializers.DecimalField(
        source='producto.precio', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    producto = ProductoSerializer(read_only=True)
    subtotal = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    
    class Meta:
        model = CarritoItem
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_precio',
            'cantidad', 'fecha_agregado', 'subtotal'
        ]
        read_only_fields = ['id', 'fecha_agregado']


class CarritoSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=False
    )
    items = CarritoItemSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cantidad_items = serializers.IntegerField(read_only=True)
    total_carrito = serializers.DecimalField(
        read_only=True, 
        max_digits=12, 
        decimal_places=2
    )
    total = serializers.ReadOnlyField(source='total_carrito')
    
    class Meta:
        model = Carrito
        fields = [
            'id', 'cliente', 'cliente_nombre', 'estado',
            'fecha_creacion', 'fecha_actualizacion', 
            'items', 'cantidad_items', 'total_carrito'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate(self, attrs):
        request = self.context.get('request')
        auth = getattr(request, 'auth', None) if request else None
        role = auth.get('role') if hasattr(auth, 'get') else None

        if self.instance is None and role != 'CLIENTE' and not attrs.get('cliente'):
            raise serializers.ValidationError({'cliente': 'Este campo es requerido.'})

        return attrs
