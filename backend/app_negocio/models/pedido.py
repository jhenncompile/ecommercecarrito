from django.db import models
from .carrito import Carrito


class Pedido(models.Model):
    """
    Modelo de Pedido (Orden de Compra).
    
    Estados:
    - PENDIENTE: Acaba de crearse
    - PROCESADO: Se está preparando
    - ENVIADO: Ya se envió
    - ENTREGADO: Cliente recibió
    - CANCELADO: Pedido cancelado
    """
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('PROCESADO', 'Procesado'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    stripe_session_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name='Stripe Session ID'
    )
    
    carrito = models.OneToOneField(
        Carrito,
        on_delete=models.CASCADE,
        related_name='pedido',
        verbose_name='Carrito'
    )
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    class Meta:
        db_table = 'app_negocio_pedido'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.carrito.cliente.nombre} ({self.estado})"
