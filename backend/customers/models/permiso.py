from django.db import models

class Permiso(models.Model):
    """
    Modelo para definir acciones específicas permitidas en el sistema.
    Ejemplos: 'CREAR_PRODUCTO', 'VER_REPORTES', 'GESTIONAR_USUARIOS'
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del Permiso'
    )
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código Identificador'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    modulo = models.CharField(
        max_length=50,
        verbose_name='Módulo al que pertenece',
        help_text='Ej: Productos, Ventas, Usuarios'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    class Meta:
        db_table = 'customers_permiso'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['modulo', 'nombre']

    def __str__(self):
        return f"{self.modulo} - {self.nombre} ({self.codigo})"
