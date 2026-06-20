from django.db import models


class PrediccionCache(models.Model):
    usuario_id = models.IntegerField(null=True, blank=True)
    usuario_email = models.EmailField(blank=True, default='')
    configuracion = models.JSONField(verbose_name='Configuración')
    resultado = models.JSONField(verbose_name='Resultado')
    hash_config = models.CharField(max_length=64, unique=True, db_index=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(verbose_name='Expira en')
    vigente = models.BooleanField(default=True)

    class Meta:
        app_label = 'cu22_gestionar_prediccion_de_ventas'
        db_table = 'app_negocio_prediccion_cache'
        verbose_name = 'Caché de Predicción'
        verbose_name_plural = 'Cachés de Predicción'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Predicción {self.hash_config[:8]} - {self.fecha_creacion}"
