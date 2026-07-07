from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.customers.clientes.models.cliente import Cliente
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto


class Resena(models.Model):
    """
    Reseña y Calificación de un producto (CU-27).

    Multi-tenant: vive en el schema de la tienda, por lo que la reseña pertenece
    a los productos de esa tienda. El cliente es un modelo compartido (public),
    replicando el patrón de Carrito.cliente y RestockRequest.cliente.

    Regla de negocio: solo pueden reseñar los compradores verificados, es decir,
    clientes con un pedido PAGADO o ENTREGADO que contenga el producto. La
    verificación se hace en el servicio antes de crear la reseña.
    """

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='resenas',
        verbose_name='Producto'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='resenas',
        verbose_name='Cliente'
    )
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Calificación (1 a 5 estrellas)'
    )
    comentario = models.TextField(
        blank=True,
        default='',
        verbose_name='Comentario'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de la Reseña'
    )

    class Meta:
        app_label = 'cu26_gestionar_resenas'
        db_table = 'app_negocio_resena'
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-created_at']
        # Una sola reseña por cliente y producto (se actualiza si ya existe).
        constraints = [
            models.UniqueConstraint(
                fields=['cliente', 'producto'],
                name='unique_resena_por_cliente_producto'
            )
        ]

    def __str__(self):
        return f"{self.cliente.nombre} -> {self.producto.nombre}: {self.calificacion}★"
