from django.db import models
from .pedido import Pedido
from customers.models.cliente import Cliente


class TipoPago(models.Model):
    """
    Modelo de Tipo de Pago.
    
    Opciones:
    - EFECTIVO
    - TARJETA_CREDITO
    - TARJETA_DEBITO
    - TRANSFERENCIA_BANCARIA
    - DEPOSITO_BANCARIO
    """
    
    nombre = models.CharField(
        max_length=60,
        verbose_name='Nombre del Tipo de Pago'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    estado = models.CharField(
        max_length=20,
        default='ACTIVO',
        choices=[
            ('ACTIVO', 'Activo'),
            ('INACTIVO', 'Inactivo'),
        ],
        verbose_name='Estado'
    )
    
    class Meta:
        db_table = 'app_negocio_tipo_pago'
        verbose_name = 'Tipo de Pago'
        verbose_name_plural = 'Tipos de Pago'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Factura(models.Model):
    """
    Modelo de Factura (Documento Legal).
    
    Estados:
    - VIGENTE: Factura activa
    - ANULADA: Factura cancelada
    """
    
    ESTADO_CHOICES = [
        ('VIGENTE', 'Vigente'),
        ('ANULADA', 'Anulada'),
    ]
    
    nro = models.CharField(
        max_length=50,
        unique=True,
        primary_key=True,
        verbose_name='Número de Factura'
    )
    fecha = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha'
    )
    hora = models.TimeField(
        auto_now_add=True,
        verbose_name='Hora'
    )
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.RESTRICT,
        related_name='factura',
        verbose_name='Pedido'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.RESTRICT,
        related_name='facturas',
        verbose_name='Cliente'
    )
    tipo_pago = models.ForeignKey(
        TipoPago,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='facturas',
        verbose_name='Tipo de Pago'
    )
    monto_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Monto Total'
    )
    moneda = models.CharField(
        max_length=10,
        default='BOB',
        verbose_name='Moneda'
    )
    cuf = models.TextField(
        blank=True,
        null=True,
        verbose_name='CUF (Código Único de Factura)'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='VIGENTE',
        verbose_name='Estado'
    )
    
    class Meta:
        db_table = 'app_negocio_factura'
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Factura {self.nro} - {self.cliente.nombre} - {self.monto_total} {self.moneda}"
