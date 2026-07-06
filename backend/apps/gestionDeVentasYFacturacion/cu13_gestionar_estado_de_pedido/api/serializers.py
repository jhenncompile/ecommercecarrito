from rest_framework import serializers
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.api.carrito_serializers import CarritoItemSerializer


class PedidoSerializer(serializers.ModelSerializer):
    carrito_id = serializers.IntegerField(source='carrito.id', read_only=True)
    cliente_nombre = serializers.CharField(source='carrito.cliente.nombre', read_only=True)
    cliente_email = serializers.CharField(source='carrito.cliente.correo', read_only=True)
    total_pedido = serializers.DecimalField(
        source='carrito.total_carrito',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    cantidad_items = serializers.IntegerField(source='carrito.cantidad_items', read_only=True)
    items = CarritoItemSerializer(source='carrito.items', many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'carrito', 'carrito_id', 'cliente_nombre', 'cliente_email', 'estado',
            'fecha_creacion', 'fecha_actualizacion', 'observaciones',
            'tipo_envio', 'costo_envio', 'ciudad_envio', 'zona_envio',
            'total_pedido', 'cantidad_items', 'items'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
