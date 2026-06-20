from django.contrib import admin
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.admin_base import PublicOnlyAdmin
from ..models import Plan


@admin.register(Plan)
class PlanAdmin(PublicOnlyAdmin):
    list_display = ('nombre', 'precio_mensual', 'precio_anual', 'max_usuarios', 'max_productos', 'activo')
    list_filter = ('activo', 'max_usuarios')
    search_fields = ('nombre',)
    filter_horizontal = ('permisos',)
    fieldsets = (
        ('InformaciÃ³n BÃ¡sica', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Precios', {
            'fields': ('precio_mensual', 'precio_anual')
        }),
        ('LÃ­mites y Permisos', {
            'fields': ('max_usuarios', 'max_productos', 'facturacion_max', 'permisos')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

