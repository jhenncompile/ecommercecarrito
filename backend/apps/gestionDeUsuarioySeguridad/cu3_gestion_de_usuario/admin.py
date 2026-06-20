from django.contrib import admin
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.admin_base import PublicOnlyAdmin
from .models.usuario import Usuario

@admin.register(Usuario)
class UsuarioAdmin(PublicOnlyAdmin):
    list_display = ('username', 'email', 'tenant')
