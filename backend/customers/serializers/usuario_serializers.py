from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

class MyTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email") or attrs.get("username")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email/usuario y contraseña son requeridos.")

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Credenciales incorrectas.")

        if not user.is_active:
            raise serializers.ValidationError("Este usuario está inactivo.")

        refresh = RefreshToken.for_user(user)
        if user.tenant:
            refresh['schema'] = user.tenant.schema_name
            refresh['tenant_name'] = user.tenant.name

        self.user = user
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class UsuarioCrudSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
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
        if obj.is_staff or obj.is_superuser:
            if obj.tenant:
                from customers.models import Domain
                domain = Domain.objects.filter(tenant=obj.tenant).first()
                return {
                    'nombre_tienda': obj.tenant.name,
                    'schema': obj.tenant.schema_name,
                    'dominio': domain.domain if domain else None,
                    'url': f"http://{domain.domain if domain else obj.tenant.schema_name}.localhost:8001" if domain else None,
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
        from customers.models.usuario import Usuario
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'tenant', 'roles', 'tenant_info', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}