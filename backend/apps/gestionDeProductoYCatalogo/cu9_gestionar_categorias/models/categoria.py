from django.db import models
from django.db import connection


class Categoria(models.Model):
    """
    Modelo de Categoría de Productos.
    
    Características:
    - Soporta subcategorías (auto-referencia)
    - Multi-tenant: cada categoría pertenece a un schema
    - Las queries se filtran automáticamente por el schema activo
    """
    
    nombre = models.CharField(
        max_length=120,
        verbose_name='Nombre de Categoría'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategorias',
        verbose_name='Categoría Principal'
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
        app_label = 'cu9_gestionar_categorias'
        db_table = 'app_negocio_categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
        # Validar que no haya duplicados por tenant
        constraints = [
            models.UniqueConstraint(
                fields=['nombre', 'parent'],
                name='unique_categoria_por_padre'
            )
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.nombre} > {self.nombre}"
        return self.nombre
    
    @property
    def ruta_completa(self):
        """Devuelve la ruta completa de la categoría (ej: Electrónica > Computadoras)"""
        if self.parent:
            return f"{self.parent.ruta_completa} > {self.nombre}"
        return self.nombre
