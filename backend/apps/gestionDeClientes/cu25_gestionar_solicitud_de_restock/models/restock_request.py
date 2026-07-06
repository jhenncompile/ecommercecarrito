from django.db import models
from apps.customers.clientes.models.cliente import Cliente
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto


class RestockRequest(models.Model):
    """
    Solicitud de Restock (CU-25 Intención de Compra).

    Registra el interés de un cliente por un producto agotado.

    Multi-tenant: vive en el schema de la tienda, por lo que pertenece
    implícitamente al tenant (negocio) correspondiente. El cliente es un
    modelo compartido (public), replicando el patrón de Carrito.cliente.
    """

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('notified', 'Notificado'),
        ('fulfilled', 'Atendido'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='restock_requests',
        verbose_name='Cliente'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='restock_requests',
        verbose_name='Producto'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Solicitud'
    )

    class Meta:
        app_label = 'cu25_gestionar_solicitud_de_restock'
        db_table = 'app_negocio_restock_request'
        verbose_name = 'Solicitud de Restock'
        verbose_name_plural = 'Solicitudes de Restock'
        ordering = ['-created_at']
        # Evitar duplicados para un mismo cliente y producto
        constraints = [
            models.UniqueConstraint(
                fields=['cliente', 'producto'],
                name='unique_restock_por_cliente_producto'
            )
        ]

    def __str__(self):
        return f"Restock {self.producto_id} por cliente {self.cliente_id} ({self.status})"
