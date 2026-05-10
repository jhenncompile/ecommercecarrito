from rest_framework import permissions

class HasPermiso(permissions.BasePermission):
    """
    Permiso personalizado que verifica si el usuario tiene el permiso específico
    en cualquiera de sus roles.
    
    Uso:
    permission_classes = [HasPermiso]
    required_permiso = 'CREAR_PRODUCTO'
    """

    def has_permission(self, request, view):
        # 1. Si no está autenticado, denegar
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Si es superusuario, permitir todo
        if getattr(request.user, 'is_superuser', False):
            return True

        # 3. Obtener el permiso requerido desde la vista
        required_permiso = getattr(view, 'required_permiso', None)
        if not required_permiso:
            return True  # Si la vista no define uno, permitir (o cambiar a False según política)

        # 4. Verificar permisos en los roles del usuario
        # Optimizamos consultando los códigos de permisos directamente
        user_permisos = request.user.roles.filter(
            activo=True, 
            permisos__activo=True
        ).values_list('permisos__codigo', flat=True).distinct()

        return required_permiso in user_permisos
