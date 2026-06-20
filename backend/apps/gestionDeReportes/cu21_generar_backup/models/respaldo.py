from django.db import models
import zlib

class RespaldoSistema(models.Model):
    """
    Guarda snapshots del sistema con estructura de lista doblemente ligada para versionado.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=100)
    archivo_path = models.CharField(max_length=255, blank=True, null=True, help_text="Ruta física en el servidor")
    blob_data = models.BinaryField(null=True, blank=True, help_text="Copia de seguridad en DB (opcional)")
    
    # Estructura de punteros (Cola y Siguiente)
    anterior = models.OneToOneField(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sucesor',
        verbose_name='Versión Anterior (Cola)'
    )
    siguiente = models.OneToOneField(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='predecesor',
        verbose_name='Versión Siguiente'
    )

    metadata = models.JSONField(default=dict, help_text="Info técnica: tablas, tamaño, etc.")

    class Meta:
        app_label = 'cu21_generar_backup'
        db_table = 'customers_respaldo'
        verbose_name = "Respaldo del Sistema"
        verbose_name_plural = "Respaldos del Sistema"
        ordering = ['timestamp']  # Cronológico

    def __str__(self):
        return f"v.{self.timestamp.strftime('%d/%m')} - {self.nombre}"


    @property
    def size_mb(self):
        if self.blob_data:
            return round(len(self.blob_data) / (1024 * 1024), 2)
        return 0


class ConfiguracionRespaldo(models.Model):
    """
    Guarda la configuración para respaldos automáticos.
    """
    FRECUENCIA_CHOICES = [
        ('DIARIO', 'Diario'),
        ('SEMANAL', 'Semanal'),
        ('MENSUAL', 'Mensual'),
    ]

    activo = models.BooleanField(default=False)
    frecuencia = models.CharField(max_length=10, choices=FRECUENCIA_CHOICES, default='DIARIO')
    hora_ejecucion = models.TimeField(help_text="Hora del día (HH:MM:SS)")
    
    # Para Semanal: 0=Lunes, 6=Domingo. Para Mensual: 1 al 31.
    dia_referencia = models.IntegerField(default=0, help_text="Día de la semana (0-6) o del mes (1-31)")

    class Meta:
        app_label = 'cu21_generar_backup'
        db_table = 'customers_configuracion_respaldo'
        verbose_name = "Configuración de Respaldo"
        verbose_name_plural = "Configuraciones de Respaldo"

    def __str__(self):
        return f"{self.frecuencia} a las {self.hora_ejecucion} (Activo: {self.activo})"
