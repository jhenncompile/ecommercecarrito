from django.db import models
from .carrito import Carrito
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto


class CarritoItem(models.Model):
    """
    Modelo de Item del Carrito.
    
    Relación muchos-a-muchos entre Carrito y Producto con cantidad.
    """
    
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Carrito'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='en_carritos',
        verbose_name='Producto'
    )
    cantidad = models.IntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    fecha_agregado = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Agregado'
    )
    
    class Meta:
        app_label = 'cu11_gestion_carrito_de_compras'
        db_table = 'app_negocio_carrito_item'
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
        unique_together = ['carrito', 'producto']  # Un producto una vez por carrito
        ordering = ['fecha_agregado']
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} en Carrito #{self.carrito.id}"
    
    @property
    def subtotal(self):
        """Retorna el subtotal de este item (precio * cantidad)"""
        return self.producto.precio * self.cantidad
