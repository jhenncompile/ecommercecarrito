from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.conf import settings
from urllib.parse import urlencode, urlparse, urlunparse
import os
from core.views import BaseViewSet
from rest_framework.decorators import action
from customers.models import Cliente, Domain
from customers.serializers.cliente_serializer import (
    ClienteSerializer,
    ClienteTokenObtainSerializer,
    build_cliente_token_response,
)
from customers.services.bitacora_service import BitacoraService
from customers.services.cliente_service import ClienteService


class ClienteSSOMixin:
    def _get_redirect_value(self, request):
        return (
            request.data.get('redirect')
            or request.query_params.get('redirect')
            or request.data.get('next')
            or request.query_params.get('next')
        )

    def _resolve_tenant_redirect(self, raw_redirect):
        """
        Valida que el retorno apunte a un dominio tenant registrado.
        Evita enviar tokens a hosts arbitrarios.
        """
        if not raw_redirect:
            return None

        raw_redirect = str(raw_redirect).strip()
        parsed = urlparse(raw_redirect if '://' in raw_redirect else f"//{raw_redirect}")
        hostname = (parsed.hostname or '').lower().strip()

        if not hostname:
            raise ValidationError({'redirect': 'Dominio de retorno inválido.'})

        domain = (
            Domain.objects
            .select_related('tenant')
            .filter(domain__iexact=hostname, tenant__activo=True)
            .first()
        )
        if not domain:
            raise ValidationError({'redirect': 'La tienda de retorno no existe o no está activa.'})

        return {
            'domain': domain.domain,
            'port': parsed.port,
        }

    def _frontend_port_from_request(self, request):
        origin = request.headers.get('Origin') or request.META.get('HTTP_REFERER')
        if origin:
            parsed = urlparse(origin)
            if parsed.port:
                return parsed.port
        return getattr(settings, 'REACT_PORT', None) or os.environ.get('REACT_PORT', '3000')

    def _build_sso_url(self, request, redirect_data, auth_data):
        origin = request.headers.get('Origin') or request.META.get('HTTP_REFERER')
        parsed_origin = urlparse(origin) if origin else None
        scheme = parsed_origin.scheme if parsed_origin and parsed_origin.scheme else ('https' if request.is_secure() else 'http')

        port = redirect_data.get('port') or self._frontend_port_from_request(request)
        default_port = (scheme == 'http' and str(port) == '80') or (scheme == 'https' and str(port) == '443')
        netloc = redirect_data['domain'] if not port or default_port else f"{redirect_data['domain']}:{port}"

        query = urlencode({
            'token': auth_data['access'],
            'refresh': auth_data['refresh'],
            'full_name': auth_data.get('cliente', {}).get('nombre', ''),
            'role': 'cliente',
        })
        return urlunparse((scheme, netloc, '/sso', '', query, ''))

    def _attach_sso_data(self, request, data):
        redirect_data = self._resolve_tenant_redirect(self._get_redirect_value(request))
        if redirect_data:
            data['redirect'] = redirect_data['domain']
            data['subdomain'] = redirect_data['domain']
            data['sso_url'] = self._build_sso_url(request, redirect_data, data)
        return data


class ClienteLoginView(ClienteSSOMixin, APIView):
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
            data = dict(serializer.validated_data)
            self._attach_sso_data(request, data)
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClienteViewSet(ClienteSSOMixin, BaseViewSet):
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
    
    @action(detail=False, methods=['get', 'patch'], url_path='perfil')
    def perfil(self, request):
        """
        Obtener o actualizar el perfil del cliente autenticado.
        """
        # El ID viene del token validado por ClienteJWTAuthentication
        cliente_id = getattr(request.user, 'cliente_id', None)
        if not cliente_id:
            return Response({"detail": "No se pudo identificar al cliente."}, status=status.HTTP_401_UNAUTHORIZED)
            
        cliente = Cliente.objects.filter(id=cliente_id).first()
        if not cliente:
            return Response({"detail": "Cliente no encontrado."}, status=status.HTTP_404_NOT_FOUND)
            
        if request.method == 'GET':
            serializer = self.get_serializer(cliente)
            return Response(serializer.data)
            
        elif request.method == 'PATCH':
            serializer = self.get_serializer(cliente, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Auditoría
            BitacoraService.registrar_accion(
                request.user,
                self.modulo_auditoria,
                "ACTUALIZAR_PERFIL",
                request=request,
                metadatos={'id': cliente.id}
            )
            return Response(serializer.data)
    
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

    def create(self, request, *args, **kwargs):
        """
        Registro público de cliente con auto-login para Escenario B.
        Mantiene los campos del cliente en la raíz y agrega access/refresh.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cliente = serializer.save()
        BitacoraService.registrar_accion(
            request.user,
            self.modulo_auditoria,
            "CREAR",
            request=request,
            metadatos={'id': cliente.id}
        )

        response_data = dict(ClienteSerializer(cliente).data)
        response_data.update(build_cliente_token_response(cliente))
        self._attach_sso_data(request, response_data)

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
