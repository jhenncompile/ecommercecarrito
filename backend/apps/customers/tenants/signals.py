from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import connection
from apps.negocio.catalogo.models.producto import Producto
from apps.customers.users.models.usuario import Usuario

@receiver(pre_save, sender=Producto)
def validate_product_limit(sender, instance, **kwargs):
    # Solo ejecutar si estamos en un schema que no es el public (es un tenant real)
    if hasattr(connection, 'tenant') and connection.schema_name != 'public':
        tenant = connection.tenant
        # Validar solo durante la creaciÃ³n
        if tenant.plan and not instance.pk:
            count = Producto.objects.count()
            if count >= tenant.plan.max_productos:
                raise ValidationError(
                    f"Límite del plan alcanzado. El plan '{tenant.plan.nombre}' permite un máximo de {tenant.plan.max_productos} productos."
                )

@receiver(pre_save, sender=Usuario)
def validate_user_limit(sender, instance, **kwargs):
    if hasattr(connection, 'tenant') and connection.schema_name != 'public':
        tenant = connection.tenant
        # Validar solo durante la creaciÃ³n
        if tenant.plan and not instance.pk:
            count = Usuario.objects.count()
            if count >= tenant.plan.max_usuarios:
                raise ValidationError(
                    f"Límite del plan alcanzado. El plan '{tenant.plan.nombre}' permite un máximo de {tenant.plan.max_usuarios} usuarios."
                )
