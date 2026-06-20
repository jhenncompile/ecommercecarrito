from django.db import models
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.factura import Factura
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto


class DetalleFactura(models.Model):
    """
    Modelo de Detalle de Factura (Líneas de la Factura).
    
    Cada línea representa un producto vendido en la factura.
    """
    
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Factura'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.RESTRICT,
        related_name='en_facturas',
        verbose_name='Producto'
    )
    cantidad = models.IntegerField(
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Unitario'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Total (cantidad * precio_unitario)'
    )
    
    class Meta:
        app_label = 'cu14_generar_facturacion'
        db_table = 'app_negocio_detalle_factura'
        verbose_name = 'Detalle de Factura'
        verbose_name_plural = 'Detalles de Factura'
        ordering = ['factura', 'id']
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - Factura {self.factura.nro}"
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente el total antes de guardar"""
        self.total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
