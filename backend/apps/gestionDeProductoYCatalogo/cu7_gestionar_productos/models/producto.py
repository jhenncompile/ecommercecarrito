from django.db import models
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.promocion import Promocion

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Costo de Compra')
    stock = models.IntegerField(default=0)
    atributos = models.JSONField(default=dict, blank=True, null=True, verbose_name='Atributos (Color, Talla, etc.)')
    
    # Cambiar de CharField a ForeignKey
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.RESTRICT,
        related_name='productos',
        verbose_name='Categoría'
    )
    
    # Relación con Promoción
    promocion = models.ForeignKey(
        Promocion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        verbose_name='Promoción'
    )
    
    activo = models.BooleanField(default=True)
    imagen_url = models.URLField(max_length=500, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'cu7_gestionar_productos'
        db_table = 'app_negocio_producto'

    def __str__(self):
        return f"{self.nombre} ({self.sku})" if self.sku else self.nombre