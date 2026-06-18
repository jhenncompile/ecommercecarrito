# apps/negocio/recordatorios/models/recordatorio.py
from django.db import models
from django.conf import settings
from apps.negocio.ordenes.models.pedido import Pedido


class Recordatorio(models.Model):
    """
    Modelo de recordatorios para el vendedor/admin de la tienda.
    Permite programar recordatorios de tareas, pagos y promociones.
    Opcionalmente puede vincularse a un Pedido (CU-13).
    Al guardarse dispara una notificación (CU-18) si está habilitado.
    """

    TIPO_CHOICES = [
        ('TAREA', 'Tarea'),
        ('PAGO', 'Pago'),
        ('PROMOCION', 'Promoción'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recordatorios',
        verbose_name='Usuario',
    )
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(blank=True, default='', verbose_name='Descripción')
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='TAREA',
        verbose_name='Tipo',
    )
    fecha_recordatorio = models.DateTimeField(verbose_name='Fecha y Hora del Evento')
    completado = models.BooleanField(default=False, verbose_name='Completado')

    # Vinculación opcional a Pedido (CU-13 Gestionar estado de pedido — extend)
    pedido = models.ForeignKey(
        Pedido,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='recordatorios',
        verbose_name='Pedido vinculado',
    )

    # Integración CU-18: enviar notificación cuando se dispara el recordatorio
    notificacion_enviada = models.BooleanField(
        default=False,
        verbose_name='Notificación enviada',
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        db_table = 'app_negocio_recordatorio'
        verbose_name = 'Recordatorio'
        verbose_name_plural = 'Recordatorios'
        ordering = ['fecha_recordatorio']

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo} — {self.fecha_recordatorio:%d/%m/%Y %H:%M}"
