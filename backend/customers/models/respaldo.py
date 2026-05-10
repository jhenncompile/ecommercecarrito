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
