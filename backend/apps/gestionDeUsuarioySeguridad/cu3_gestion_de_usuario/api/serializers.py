from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from apps.customers.models import Rol

class UsuarioCrudSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(many=True, queryset=Rol.objects.all(), required=False)
    roles_detalles = serializers.SerializerMethodField()
    tenant_info = serializers.SerializerMethodField()
    
    def get_roles_detalles(self, obj):
        """Devuelve lista de roles con manejo de errores"""
        try:
            return [{'id': r.id, 'nombre': r.nombre} for r in obj.roles.all()]
        except Exception:
            return []
    
    def get_tenant_info(self, obj):
        """Devuelve info del tenant solo si es admin/superusuario"""
        is_staff = obj.get('is_staff', False) if isinstance(obj, dict) else obj.is_staff
        is_superuser = obj.get('is_superuser', False) if isinstance(obj, dict) else obj.is_superuser
        
        if is_staff or is_superuser:
            try:
                tenant = obj.get('tenant') if isinstance(obj, dict) else obj.tenant
            except Exception: # Captura Client.DoesNotExist si la BD tiene inconsistencias
                tenant = None
                
            if tenant:
                # Si el tenant es solo el ID (por validación en POST), devolvemos None,
                # ya que no podemos acceder a tenant.name. Se mostrará correctamente en el próximo GET.
                if isinstance(tenant, int):
                    return None
                    
                from apps.customers.models import Domain
                domain = Domain.objects.filter(tenant=tenant).first()
                return {
                    'nombre_tienda': getattr(tenant, 'name', ''),
                    'schema': getattr(tenant, 'schema_name', ''),
                    'dominio': domain.domain if domain else None,
                    'url': f"http://{domain.domain if domain else getattr(tenant, 'schema_name', '')}.localhost:8001" if domain else None,
                }
        return None
    
    def validate_password(self, value):
        """Validador de contraseña fuerte"""
        import re
        if value:
            if len(value) < 8:
                raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
            if not re.search(r"[A-Z]", value):
                raise serializers.ValidationError("La contraseña debe incluir al menos una letra mayúscula.")
            if not re.search(r"[a-z]", value):
                raise serializers.ValidationError("La contraseña debe incluir al menos una letra minúscula.")
            if not re.search(r"\d", value):
                raise serializers.ValidationError("La contraseña debe incluir al menos un número.")
            if not re.search(r"[@$!%*?&]", value):
                raise serializers.ValidationError("La contraseña debe incluir al menos un carácter especial (@$!%*?&).")
        return value

    class Meta:
        from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.models.usuario import Usuario
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'tenant', 'roles', 'roles_detalles', 'tenant_info', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}