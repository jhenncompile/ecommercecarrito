from django.db import models
from django.conf import settings
from apps.customers.clientes.models.cliente import Cliente

class DeviceToken(models.Model):
    """
    Guarda los tokens FCM de los dispositivos móviles para enviar Push Notifications.
    Puede estar asociado a un Cliente (App Cliente) o a un Usuario (App Vendedor).
    """
    cliente = models.ForeignKey(
        Cliente, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='device_tokens'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='device_tokens'
    )
    token = models.CharField(max_length=255, unique=True, verbose_name="FCM Token")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'customers'
        db_table = 'customers_device_token'
        verbose_name = 'Device Token'
        verbose_name_plural = 'Device Tokens'

    def __str__(self):
        return f"Token para {'Cliente ' + str(self.cliente.id) if self.cliente else 'Usuario ' + str(self.usuario.id)}"
