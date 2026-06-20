from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.api.tipo_pago_serializer import TipoPagoSerializer
from rest_framework import serializers
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.factura import Factura, TipoPago
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.detalle_factura import DetalleFactura


class DetalleFacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleFactura
        fields = '__all__'

class FacturaSerializer(serializers.ModelSerializer):
    detalles = DetalleFacturaSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_correo = serializers.CharField(source='cliente.correo', read_only=True)
    tipo_pago_nombre = serializers.CharField(source='tipo_pago.nombre', read_only=True, allow_null=True)
    
    class Meta:
        model = Factura
        fields = [
            'nro', 'fecha', 'hora', 'pedido', 'cliente', 'cliente_nombre',
            'cliente_correo', 'tipo_pago', 'tipo_pago_nombre', 'monto_total',
            'moneda', 'cuf', 'estado', 'detalles'
        ]
        read_only_fields = ['nro', 'fecha', 'hora']
