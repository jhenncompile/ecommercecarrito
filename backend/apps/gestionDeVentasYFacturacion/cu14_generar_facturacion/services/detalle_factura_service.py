from apps.core.services import BaseService
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.detalle_factura import DetalleFactura


class DetalleFacturaService(BaseService):
    """Servicio de Detalles de Factura."""
    
    def __init__(self):
        super().__init__(DetalleFactura)
    
    def obtener_por_factura(self, factura_nro):
        """Obtiene todos los detalles de una factura."""
        return DetalleFactura.objects.filter(factura__nro=factura_nro).order_by('id')
    
    def obtener_por_producto(self, producto_id):
        """Obtiene en qué facturas se vendió un producto."""
        return DetalleFactura.objects.filter(producto_id=producto_id).order_by('-factura__fecha')
    
    def calcular_total_factura(self, factura_nro):
        """Calcula el monto total de una factura (suma de detalles)."""
        from django.db.models import Sum
        total = DetalleFactura.objects.filter(
            factura__nro=factura_nro
        ).aggregate(total=Sum('total'))['total']
        return total or 0
