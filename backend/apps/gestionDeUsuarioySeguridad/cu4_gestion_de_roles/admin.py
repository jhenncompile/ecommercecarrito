from django.contrib import admin
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.admin_base import PublicOnlyAdmin
from .models.rol import Rol


@admin.register(Rol)
class RolAdmin(PublicOnlyAdmin):
    list_display = ('nombre', 'nivel', 'activo', 'descripcion')
    list_filter = ('activo', 'nivel')
    search_fields = ('nombre',)
    ordering = ('nivel',)

