from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from core.views import BaseViewSet
from customers.models import Cliente
from customers.serializers.cliente_serializer import ClienteSerializer, ClienteTokenObtainSerializer
from customers.services.cliente_service import ClienteService


class ClienteLoginView(APIView):
    """
    Vista pública de login para Clientes.
    
    POST /api/clientes/login/
    Body:
    {
        "correo": "cliente@example.com",
        "contrasena": "micontraseña123"
    }
    
    Response:
    {
        "access": "<token_acceso>",
        "refresh": "<token_refresco>",
        "cliente": {
            "id": 1,
            "nombre": "John Doe",
            "correo": "cliente@example.com",
            "telefono": "3123456789",
            "nit": "1234567"
        }
    }
    """
    permission_classes = [AllowAny]  # Público, no requiere token previo
    authentication_classes = []  # Evita que intente validar sesiones globales previas

    def post(self, request, *args, **kwargs):
        serializer = ClienteTokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClienteViewSet(BaseViewSet):
    """
    API de Clientes (Customers).
    
    - GET /api/clientes/ - Listar todos
    - POST /api/clientes/ - Crear nuevo (público)
    - GET /api/clientes/{id}/ - Detalle
    - PUT /api/clientes/{id}/ - Actualizar
    - DELETE /api/clientes/{id}/ - Eliminar
    
    El registro es público (AllowAny en create), el resto requiere autenticación.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    modulo_auditoria = "Cliente"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ClienteService()
    
    def get_permissions(self):
        """
        Permitir registro anónimo, proteger el resto del CRUD.
        """
        from rest_framework.permissions import IsAuthenticated
        
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
