from django.db import models

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
        verbose_name='DescripciÃ³n'
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
        app_label = 'cu12_gestionar_metodos_de_pago'
    
    def __str__(self):
        return self.nombre
