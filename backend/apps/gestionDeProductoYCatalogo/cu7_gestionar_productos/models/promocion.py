from django.db import models
from datetime import date


class Promocion(models.Model):
    """
    Modelo de Promoción.
    
    Permite crear descuentos temporales para productos.
    """
    
    nombre = models.CharField(
        max_length=120,
        verbose_name='Nombre de Promoción'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    descuento_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Descuento (%)'
    )
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    fecha_fin = models.DateField(
        verbose_name='Fecha de Fin'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        app_label = 'cu7_gestionar_productos'
        db_table = 'app_negocio_promocion'
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.nombre} ({self.descuento_pct}% - {self.fecha_inicio} a {self.fecha_fin})"
    
    @property
    def vigente(self):
        """Retorna True si la promoción está activa en este momento"""
        hoy = date.today()
        return self.activo and self.fecha_inicio <= hoy <= self.fecha_fin
