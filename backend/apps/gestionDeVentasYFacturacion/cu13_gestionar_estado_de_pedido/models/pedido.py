from django.db import models
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito import Carrito


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

    TIPO_ENVIO_CHOICES = [
        ('LOCAL', 'Delivery Local'),
        ('ENCOMIENDA', 'Envío por Encomienda (Pago en Destino)'),
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

    # Logística y Envíos (CU-24)
    tipo_envio = models.CharField(
        max_length=20,
        choices=TIPO_ENVIO_CHOICES,
        blank=True,
        null=True,
        verbose_name='Tipo de Envío'
    )
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Costo de Envío'
    )
    ciudad_envio = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ciudad de Envío'
    )
    zona_envio = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name='Zona de Delivery'
    )

    class Meta:
        app_label = 'cu13_gestionar_estado_de_pedido'
        db_table = 'app_negocio_pedido'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.carrito.cliente.nombre} ({self.estado})"
