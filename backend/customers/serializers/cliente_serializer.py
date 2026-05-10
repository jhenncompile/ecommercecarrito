from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from ..models.cliente import Cliente


def build_cliente_token_response(cliente):
    """Construye la respuesta JWT pública para un Cliente."""
    refresh = RefreshToken()

    # user_id se mantiene para compatibilidad con consumidores existentes.
    refresh['user_id'] = cliente.id
    refresh['cliente_id'] = cliente.id
    refresh['role'] = 'CLIENTE'
    refresh['correo'] = cliente.correo
    refresh['nombre'] = cliente.nombre

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'cliente': {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'correo': cliente.correo,
            'telefono': cliente.telefono,
            'nit': cliente.nit,
        }
    }


class ClienteSerializer(serializers.ModelSerializer):
    contrasena = serializers.CharField(write_only=True, required=False, min_length=6)
    password = serializers.CharField(write_only=True, required=False, min_length=6)
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'nombre', 'correo', 'telefono', 'contrasena', 'password',
            'nit', 'fecha_registro', 'activo'
        ]
        read_only_fields = ['id', 'fecha_registro']

    def validate(self, attrs):
        if self.instance is None and not (attrs.get('contrasena') or attrs.get('password')):
            raise serializers.ValidationError({'contrasena': 'La contraseña es requerida.'})
        return attrs
    
    def create(self, validated_data):
        """Al crear, encriptar la contraseña."""
        contrasena = validated_data.pop('contrasena', None)
        password_alias = validated_data.pop('password', None)
        password = contrasena or password_alias
        cliente = Cliente.objects.create(**validated_data)
        cliente.set_password(password)
        return cliente


class ClienteTokenObtainSerializer(serializers.Serializer):
    """
    Serializador JWT customizado para autenticación de Clientes.
    
    Genera un token JWT con claims específicos para identificar
    al cliente dentro del sistema multi-tenant.
    """
    correo = serializers.EmailField()
    contrasena = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    redirect = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def validate(self, attrs):
        correo = attrs.get('correo')
        contrasena = attrs.get('contrasena') or attrs.get('password')

        if not contrasena:
            raise serializers.ValidationError("Contraseña requerida.")

        try:
            # Buscamos al cliente en el esquema público
            cliente = Cliente.objects.get(correo=correo, activo=True)
        except Cliente.DoesNotExist:
            raise serializers.ValidationError("No existe un cliente activo con este correo.")

        # Verificamos la contraseña (el modelo usa PBKDF2 via make_password)
        if not cliente.check_password(contrasena):
            raise serializers.ValidationError("Contraseña incorrecta.")

        return build_cliente_token_response(cliente)
