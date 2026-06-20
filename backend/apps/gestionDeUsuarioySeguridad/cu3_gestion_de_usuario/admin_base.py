from django.contrib import admin

class PublicOnlyAdmin(admin.ModelAdmin):
    """Lógica base para modelos que solo se ven en el esquema público por administradores globales."""
    
    def _is_global_admin(self, request):
        # Un admin global es aquel que está autenticado y NO está atado a ninguna tienda específica 
        # (su tenant es None, o es el esquema 'public')
        if not request.user.is_authenticated:
            return False
        return request.user.tenant is None or request.user.tenant.schema_name == 'public'

    def has_module_permission(self, request):
        # 1. ¿Estamos en la URL correcta? (Usamos getattr por seguridad)
        tenant = getattr(request, 'tenant', None)
        if not tenant or tenant.schema_name != 'public':
            return False
        # 2. ¿El usuario tiene permiso de ver esto?
        if not self._is_global_admin(request):
            return False
        return super().has_module_permission(request)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        tenant = getattr(request, 'tenant', None)
        if tenant and tenant.schema_name == 'public' and self._is_global_admin(request):
            return qs
        return qs.none()

    # Bloqueamos estrictamente el CRUD para usuarios de tiendas
    def has_view_permission(self, request, obj=None):
        return self._is_global_admin(request)

    def has_add_permission(self, request):
        return self._is_global_admin(request)

    def has_change_permission(self, request, obj=None):
        return self._is_global_admin(request)

    def has_delete_permission(self, request, obj=None):
        return self._is_global_admin(request)
from django.contrib import admin

class PublicOnlyAdmin(admin.ModelAdmin):
    """Para modelos globales (Client, Domain)."""
    def has_module_permission(self, request):
        tenant = getattr(request, 'tenant', None)
        return tenant and tenant.schema_name == 'public'

class TenantSafeAdmin(admin.ModelAdmin):
    """
    Clase Maestra de Seguridad: 
    Asegura que los datos de una tienda sean invisibles para otra.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        tenant = getattr(request, 'tenant', None)
        if not request.user.is_authenticated or request.user.tenant != tenant:
            return qs.none()
        return qs

    def has_add_permission(self, request):
        tenant = getattr(request, 'tenant', None)
        return request.user.is_authenticated and request.user.tenant == tenant

    def has_change_permission(self, request, obj=None):
        tenant = getattr(request, 'tenant', None)
        return request.user.is_authenticated and request.user.tenant == tenant

    def has_delete_permission(self, request, obj=None):
        tenant = getattr(request, 'tenant', None)
        return request.user.is_authenticated and request.user.tenant == tenant

    def has_view_permission(self, request, obj=None):
        tenant = getattr(request, 'tenant', None)
        return request.user.is_authenticated and request.user.tenant == tenant