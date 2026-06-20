from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.models.tipo_pago import TipoPago
from django.db import models
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.customers.clientes.models.cliente import Cliente




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
        app_label = 'cu14_generar_facturacion'
        db_table = 'app_negocio_factura'
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Factura {self.nro} - {self.cliente.nombre} - {self.monto_total} {self.moneda}"
