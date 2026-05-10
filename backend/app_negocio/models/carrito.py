from django.db import models
from django.db import connection
from customers.models.cliente import Cliente


class Carrito(models.Model):
    """
    Modelo de Carrito de Compras.
    
    Estados:
    - ABIERTO: Cliente está agregando items
    - CERRADO: Cliente finalizó la compra (se creó un Pedido)
    - ABANDONADO: Cliente no terminó la compra
    """
    
    ESTADO_CHOICES = [
        ('ABIERTO', 'Abierto'),
        ('CERRADO', 'Cerrado'),
        ('ABANDONADO', 'Abandonado'),
    ]
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='carritos',
        verbose_name='Cliente'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ABIERTO',
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
    
    class Meta:
        db_table = 'app_negocio_carrito'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Carrito #{self.id} - {self.cliente.nombre} ({self.estado})"
    
    @property
    def cantidad_items(self):
        """Retorna la cantidad total de items en el carrito"""
        return self.items.aggregate(
            total=models.Sum('cantidad')
        )['total'] or 0
    
    @property
    def total_carrito(self):
        """Retorna el monto total del carrito"""
        return self.items.aggregate(
            total=models.Sum(
                models.F('producto__precio') * models.F('cantidad'),
                output_field=models.DecimalField()
            )
        )['total'] or 0
