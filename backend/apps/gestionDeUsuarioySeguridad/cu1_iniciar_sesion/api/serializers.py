from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings

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
        if hasattr(user, 'tenant') and user.tenant:
            refresh['schema'] = user.tenant.schema_name
            refresh['tenant_name'] = user.tenant.name

        self.user = user
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class DualTokenRefreshSerializer(serializers.Serializer):
    """Refresca el access token para AMBOS tipos de identidad (Usuario y Cliente).

    El problema: existen dos JWT distintos en el sistema:
      - Usuario (vendedores/staff): user_id apunta a customers.Usuario.
      - Cliente (compradores): el token trae user_id = cliente.id + role='CLIENTE'
        + cliente_id, pero NO existe un Usuario con ese id.

    El TokenRefreshSerializer estándar de SimpleJWT hace un
    get_user_model().objects.get(id=user_id) para validar que el usuario siga
    activo. Con un token de Cliente eso lanza Usuario.DoesNotExist (uncaught) y
    provoca un 500. Aquí distinguimos por el claim 'role'/'cliente_id':

      - Cliente  -> emitimos el nuevo access sin tocar la tabla Usuario. Los
                    claims personalizados (cliente_id, role, correo, nombre) se
                    copian solos al access token.
      - Usuario  -> comportamiento normal, pero si el usuario ya no existe o está
                    inactivo devolvemos 401 (InvalidToken), nunca 500.
    """
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs['refresh'])
        except TokenError as e:
            raise InvalidToken(str(e))

        es_cliente = (
            refresh.payload.get('role') == 'CLIENTE'
            or refresh.payload.get('cliente_id') is not None
        )

        if not es_cliente:
            # Token de Usuario (vendedor/staff): validar que siga vigente.
            user_id = refresh.payload.get(jwt_settings.USER_ID_CLAIM)
            if user_id is not None:
                try:
                    user = get_user_model().objects.get(
                        **{jwt_settings.USER_ID_FIELD: user_id}
                    )
                except get_user_model().DoesNotExist:
                    raise InvalidToken('El usuario del token ya no existe.')
                if not getattr(user, 'is_active', True):
                    raise InvalidToken('El usuario está inactivo.')

        data = {'access': str(refresh.access_token)}

        # Respetamos rotación/blacklist si algún día se configuran en SIMPLE_JWT.
        if jwt_settings.ROTATE_REFRESH_TOKENS:
            if jwt_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            data['refresh'] = str(refresh)

        return data
