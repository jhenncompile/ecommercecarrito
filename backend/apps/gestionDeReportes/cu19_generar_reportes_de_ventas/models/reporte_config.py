from django.db import models

class ReporteConfig(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Reporte")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    configuracion = models.JSONField(
        verbose_name="Configuración JSON",
        help_text="Guarda dimensiones, métricas, filtros y agrupaciones."
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'cu19_generar_reportes_de_ventas'
        db_table = 'app_negocio_reporte_config'
        verbose_name = 'Configuración de Reporte'
        verbose_name_plural = 'Configuraciones de Reportes'
        ordering = ['-creado_en']

    def __str__(self):
        return self.nombre
