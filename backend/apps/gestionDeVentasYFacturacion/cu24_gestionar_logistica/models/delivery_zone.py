from django.db import models


class DeliveryZone(models.Model):
    """
    Zona de Delivery de la tienda (CU-24 Logística y Envíos).

    Características:
    - Multi-tenant: cada zona vive en el schema de su tienda, por lo que
      pertenece automáticamente al tenant correspondiente (sin FK a Client).
    - Representa un área de reparto local con un costo fijo de envío.
    """

    zone_name = models.CharField(
        max_length=120,
        verbose_name='Nombre de la Zona'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Precio de Envío'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        app_label = 'cu24_gestionar_logistica'
        db_table = 'app_negocio_delivery_zone'
        verbose_name = 'Zona de Delivery'
        verbose_name_plural = 'Zonas de Delivery'
        ordering = ['zone_name']
        constraints = [
            models.UniqueConstraint(
                fields=['zone_name'],
                name='unique_delivery_zone_por_tenant'
            )
        ]

    def __str__(self):
        return f"{self.zone_name} (Bs. {self.price})"
