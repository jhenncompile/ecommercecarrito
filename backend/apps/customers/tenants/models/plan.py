from django.db import models


class Plan(models.Model):
    """
    Modelo de Plan de Suscripción (SaaS).
    
    Define los límites y precio de cada plan que puede usar un Tenant.
    Ubicado en customers porque es infraestructura SaaS compartida, no de negocio específico.
    """
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del Plan'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    precio_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Mensual'
    )
    precio_anual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Anual'
    )
    max_usuarios = models.IntegerField(
        verbose_name='Máximo de Usuarios'
    )
    max_productos = models.IntegerField(
        verbose_name='Máximo de Productos'
    )
    ventas_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Límite de Ventas Diarias'
    )
    facturacion_max = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Límite de Facturación Diaria'
    )
    permisos = models.ManyToManyField(
        'customers.Permiso',
        blank=True,
        related_name='planes',
        verbose_name='Permisos Incluidos',
        help_text='Funcionalidades (permisos premium) que desbloquea este plan.'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'customers_plan'
        verbose_name = 'Plan de Suscripción'
        verbose_name_plural = 'Planes de Suscripción'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio_mensual}/mes"
