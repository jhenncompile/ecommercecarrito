from django.contrib import admin
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.admin_base import TenantSafeAdmin
from .models.producto import Producto

@admin.register(Producto)
class ProductoAdmin(TenantSafeAdmin):
    list_display = ('nombre', 'precio', 'stock')
    search_fields = ('nombre',)
