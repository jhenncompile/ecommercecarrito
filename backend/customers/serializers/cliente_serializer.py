from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from customers.models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    contrasena = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'nombre', 'correo', 'telefono', 'contrasena',
            'nit', 'fecha_registro', 'activo'
        ]
        read_only_fields = ['id', 'fecha_registro']
    
    def create(self, validated_data):
        """Al crear, encriptar la contraseña."""
        password = validated_data.pop('contrasena', None)
        cliente = Cliente.objects.create(**validated_data)
        if password:
            cliente.set_password(password)
        return cliente


class ClienteTokenObtainSerializer(serializers.Serializer):
    """
    Serializador JWT customizado para autenticación de Clientes.
    
    Genera un token JWT con claims específicos para identificar
    al cliente dentro del sistema multi-tenant.
    """
    correo = serializers.EmailField()
    contrasena = serializers.CharField(write_only=True)

    def validate(self, attrs):
        correo = attrs.get('correo')
        contrasena = attrs.get('contrasena')

        try:
            # Buscamos al cliente en el esquema público
            cliente = Cliente.objects.get(correo=correo, activo=True)
        except Cliente.DoesNotExist:
            raise serializers.ValidationError("No existe un cliente activo con este correo.")

        # Verificamos la contraseña (el modelo usa PBKDF2 via make_password)
        if not cliente.check_password(contrasena):
            raise serializers.ValidationError("Contraseña incorrecta.")

        # Generamos el token manualmente para el Cliente
        refresh = RefreshToken()
        
        # Inyectamos datos clave en el payload del JWT
        # user_id para compatibilidad con DRF
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
