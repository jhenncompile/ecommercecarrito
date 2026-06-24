from rest_framework import permissions
from django.db import connection

class HasPermiso(permissions.BasePermission):
    """
    Permiso personalizado que verifica si:
    1. El usuario tiene el permiso específico en cualquiera de sus roles.
    2. El Plan activo del Tenant actual incluye dicho permiso (si el permiso no es básico).
    """

    def has_permission(self, request, view):
        # 1. Si no está autenticado, denegar
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Si es superusuario, permitir todo
        if getattr(request.user, 'is_superuser', False):
            return True

        # 3. Obtener el permiso requerido desde la vista
        required_permiso_codigo = getattr(view, 'required_permiso', None)
        if not required_permiso_codigo:
            return True  # Si la vista no define uno, permitir

        # 4. Validar límite de plan de suscripción (Solo para Tenants)
        schema_name = connection.schema_name
        if schema_name != 'public':
            from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.models.permiso import Permiso
            from apps.customers.tenants.models.tenant import Client
            
            try:
                permiso_obj = Permiso.objects.get(codigo=required_permiso_codigo)
                # Si no es básico, se debe validar contra el Plan de la tienda
                if not permiso_obj.es_basico:
                    tenant = Client.objects.get(schema_name=schema_name)
                    plan = tenant.plan
                    
                    # Si no tiene plan o el plan está inactivo, no permite permisos premium
                    if not plan or not plan.activo:
                        return False
                        
                    # Verificación Lazy de Expiración
                    import datetime
                    hoy = datetime.date.today()
                    if tenant.fecha_fin_suscripcion and tenant.fecha_fin_suscripcion < hoy:
                        # La suscripción expiró. Degradamos automáticamente al plan gratis (precio 0)
                        from apps.customers.tenants.models.plan import Plan
                        plan_gratis = Plan.objects.filter(precio_mensual=0).first()
                        if plan_gratis:
                            tenant.plan = plan_gratis
                            tenant.fecha_inicio_suscripcion = None
                            tenant.fecha_fin_suscripcion = None
                            tenant.save()
                            # Actualizamos la variable local plan para el resto de la validación
                            plan = plan_gratis
                        else:
                            return False # No se puede continuar sin plan válido
                            
                        # Si acaba de ser degradado a gratis, seguramente no tiene este permiso
                        if not plan.permisos.filter(codigo=required_permiso_codigo).exists():
                            return False
                        
                    # Verificar si el plan incluye la funcionalidad
                    if not plan.permisos.filter(codigo=required_permiso_codigo).exists():
                        return False
            except Permiso.DoesNotExist:
                return False
            except Client.DoesNotExist:
                return False

        # 5. Verificar permisos en los roles del usuario
        user_permisos = request.user.roles.filter(
            activo=True, 
            permisos__activo=True
        ).values_list('permisos__codigo', flat=True).distinct()

        return required_permiso_codigo in user_permisos
