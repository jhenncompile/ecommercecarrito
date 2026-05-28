from django.contrib import admin
from apps.customers.admin.base import PublicOnlyAdmin
from .models.permiso import Permiso

@admin.register(Permiso)
class PermisoAdmin(PublicOnlyAdmin):
    list_display = ('nombre', 'codigo', 'modulo', 'es_basico', 'activo')
    list_filter = ('es_basico', 'activo', 'modulo')
    search_fields = ('nombre', 'codigo', 'modulo')
    ordering = ('modulo', 'nombre')
