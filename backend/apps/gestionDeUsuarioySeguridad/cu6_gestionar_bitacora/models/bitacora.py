from django.db import models
from django.conf import settings

class Bitacora(models.Model):
    idUsuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='idUsuario',
        verbose_name='Usuario'
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora')
    accion = models.CharField(max_length=50, verbose_name='Acción')
    modulo = models.CharField(max_length=100, verbose_name='Módulo')
    metadatos = models.JSONField(null=True, blank=True, verbose_name='Metadatos')

    class Meta:
        app_label = 'customers'
        db_table = 'customers_bitacora'
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha}"

    @property
    def usuario(self):
        return self.idUsuario
