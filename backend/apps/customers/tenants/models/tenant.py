from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from .plan import Plan

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True
    
    # Relación con Plan de suscripción
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes',
        verbose_name='Plan de Suscripción'
    )
    
    # Fechas de suscripción
    fecha_inicio_suscripcion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Inicio de Suscripción'
    )
    
    fecha_fin_suscripcion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Fin de Suscripción'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    limite_alcanzado_fecha = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Límite Alcanzado'
    )
    
    # Campos comerciales para el Marketplace (Escenario C)
    nombre_comercial = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Nombre Comercial de la Tienda'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción de la Tienda'
    )
    
    categoria_tienda = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Categoría de la Tienda'
    )
    
    logo_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL del Logo de la Tienda'
    )
    
    icono = models.ImageField(
        upload_to='tiendas/iconos/',
        null=True,
        blank=True,
        verbose_name='Icono de la Tienda'
    )

    # Configuración de Logística y Envíos
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ciudad de la Tienda'
    )

    whatsapp = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='Número de WhatsApp de la Tienda'
    )

    enable_local_delivery = models.BooleanField(
        default=False,
        verbose_name='Habilitar Delivery Local'
    )

    enable_national_shipping = models.BooleanField(
        default=True,
        verbose_name='Habilitar Envío Nacional (Encomienda)'
    )

class Domain(DomainMixin):
    pass