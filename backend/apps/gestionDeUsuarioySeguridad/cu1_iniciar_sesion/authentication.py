from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class ClienteTokenUser:
    """
    Usuario liviano para requests autenticados con JWT de Cliente.
    No representa un Usuario vendedor; solo habilita permisos DRF.
    """

    role = "CLIENTE"
    is_active = True

    def __init__(self, token):
        self.token = token
        self.cliente_id = token.get("cliente_id") or token.get("user_id")
        self.id = self.cliente_id
        self.pk = self.cliente_id
        self.correo = token.get("correo", "")
        self.email = self.correo
        self.nombre = token.get("nombre", "")

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_username(self):
        return self.correo

    def __str__(self):
        return self.correo or f"Cliente {self.cliente_id}"


class ClienteJWTAuthentication(JWTAuthentication):
    """
    Autentica tokens emitidos por /api/clientes/login/.

    Los clientes no son AUTH_USER_MODEL; por eso no deben pasar por la
    autenticación JWT estándar que busca un customers.Usuario.
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        if validated_token.get("role") != "CLIENTE":
            return None

        if not validated_token.get("cliente_id"):
            raise InvalidToken("Token de cliente sin cliente_id.")

        return ClienteTokenUser(validated_token), validated_token


class UsuarioJWTAuthentication(JWTAuthentication):
    """
    JWT estándar de usuarios internos.

    Rechaza tokens de Cliente para que no puedan autenticarse como vendedores
    por coincidencia de IDs contra AUTH_USER_MODEL.
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        if validated_token.get("role") == "CLIENTE":
            return None

        return self.get_user(validated_token), validated_token

    def get_user(self, validated_token):
        if validated_token.get("role") == "CLIENTE":
            raise InvalidToken("Token de cliente no permitido en este endpoint.")
        return super().get_user(validated_token)
