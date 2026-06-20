from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

# Imports de Core y Servicios
from apps.core.views import BaseViewSet
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.services.usuario_service import UsuarioService
from apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.services.auth_service import get_auth_extra_data
from apps.gestionDeUsuarioySeguridad.cu6_gestionar_bitacora.services.bitacora_service import BitacoraService

# Modelos y Serializadores
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.models.usuario import Usuario
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.api.serializers import (
    
    UsuarioCrudSerializer
)
from apps.customers.tenants.api.serializers import TenantCreateSerializer



class UsuarioCrudViewSet(BaseViewSet):
    """
    Vista de usuarios refactorizada. 
    Hereda de BaseViewSet para auditorÃ­a y multi-tenant automÃ¡ticos.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioCrudSerializer
    modulo_auditoria = "Usuario"

    def get_queryset(self):
        from django.db import connection
        qs = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser:
            if connection.schema_name != 'public':
                return qs.filter(tenant__schema_name=connection.schema_name)
            return qs
            
        if user.tenant:
            return qs.filter(tenant=user.tenant)
            
        return qs.none()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = UsuarioService()

    def perform_create(self, serializer):
        from django.db import connection
        from apps.customers.models import Client
        
        datos = serializer.validated_data.copy()
        
        # AsignaciÃ³n automÃ¡tica de tenant si estamos en una tienda
        if connection.schema_name != 'public' and not datos.get('tenant'):
            tenant = Client.objects.get(schema_name=connection.schema_name)
            datos['tenant'] = tenant
            
        return self.service.crear_usuario(datos)

    def perform_update(self, serializer):
        target_user = self.get_object()
        request_user = self.request.user
        
        # Proteger a los administradores/dueños
        if target_user.is_staff or target_user.is_superuser:
            if not (request_user.is_staff or request_user.is_superuser) and target_user != request_user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("No tienes permisos para modificar a un administrador o dueño de la tienda.")
                
        return self.service.actualizar_usuario(target_user, serializer.validated_data)

    def perform_destroy(self, instance):
        request_user = self.request.user
        if instance.is_staff or instance.is_superuser:
            if not (request_user.is_staff or request_user.is_superuser) and instance != request_user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("No tienes permisos para eliminar a un administrador o dueño de la tienda.")
        super().perform_destroy(instance)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        usuario = self.get_object()
        return Response({'id': usuario.id, 'is_active': usuario.is_active})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        usuario = self.get_object()
        self.service.activar(usuario)
        
        # El Mixin detecta el .save() interno del servicio para auditorÃ­a
        return Response({'detail': 'Usuario activado exitosamente', 'is_active': True})

    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        usuario = self.get_object()
        self.service.desactivar(usuario)
        
        return Response({'detail': 'Usuario desactivado exitosamente', 'is_active': False})


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PERFIL DEL USUARIO AUTENTICADO
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class MiPerfilView(APIView):
    """
    Obtener y actualizar el perfil del usuario autenticado.
    
    GET /api/usuarios/perfil/ â†’ Obtener datos del perfil
    PATCH /api/usuarios/perfil/ â†’ Actualizar datos
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener datos del perfil del usuario autenticado"""
        usuario = request.user
        
        # Si es un cliente (usuario liviano del token)
        if hasattr(usuario, 'role') and usuario.role == "CLIENTE":
            return Response({
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.correo,
                'role': usuario.role,
                'is_cliente': True
            }, status=status.HTTP_200_OK)

        # Si es un vendedor/admin (Usuario real del modelo)
        try:
            serializer = UsuarioCrudSerializer(usuario)
            data = serializer.data
            
            # --- INCORPORACIÓN DE PERMISOS EFECTIVOS ---
            from django.db import connection
            from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.models.permiso import Permiso
            from apps.customers.tenants.models.tenant import Client
            
            if usuario.is_superuser:
                permisos_premium = set(Permiso.objects.filter(es_basico=False, activo=True).values_list('codigo', flat=True))
                user_permisos_basicos = set(Permiso.objects.filter(es_basico=True, activo=True).values_list('codigo', flat=True))
            else:
                user_permisos = Permiso.objects.filter(roles__usuarios=usuario, roles__activo=True, activo=True)
                permisos_premium = set(user_permisos.filter(es_basico=False).values_list('codigo', flat=True))
                user_permisos_basicos = set(user_permisos.filter(es_basico=True).values_list('codigo', flat=True))
            
            schema_name = connection.schema_name
            if schema_name != 'public':
                try:
                    tenant = Client.objects.get(schema_name=schema_name)
                    if tenant.plan and tenant.plan.activo:
                        plan_permisos = set(tenant.plan.permisos.filter(activo=True).values_list('codigo', flat=True))
                        if usuario.is_superuser:
                            permisos_efectivos_premium = permisos_premium
                        else:
                            permisos_efectivos_premium = permisos_premium & plan_permisos
                    else:
                        permisos_efectivos_premium = permisos_premium if usuario.is_superuser else set()
                except Client.DoesNotExist:
                    permisos_efectivos_premium = set()
            else:
                permisos_efectivos_premium = permisos_premium

            data['permisos_efectivos'] = list(user_permisos_basicos | permisos_efectivos_premium)
            # ---------------------------------------------
            
            # Determinar rol dinámico para el frontend (prioridad jerárquica)
            if usuario.is_superuser:
                data['role'] = 'admin'
            else:
                data['role'] = 'vendedor'
            
            # Asegurar que el frontend sepa si es superuser
            data['is_superuser'] = usuario.is_superuser
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            return Response({
                'error': 'Error al procesar el perfil del usuario',
                'detail': str(e),
                'traceback': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        """Actualizar datos del perfil"""
        usuario = request.user
        serializer = UsuarioCrudSerializer(
            usuario,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email requerido'}, status=400)

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({'message': 'Si el email existe, recibirÃ¡s un enlace.'})

        host = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{protocol}://{host}/reset-password/{uid}/{token}/"

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            return Response({
                'message': 'Email no configurado en el servidor.',
                'dev_reset_url': reset_url
            }, status=503 if not settings.DEBUG else 200)

        try:
            send_email_ssl(
                to_email=email,
                subject='Restablecer contraseÃ±a',
                body=f'Haz clic aquÃ­ para restablecer tu contraseÃ±a:\n\n{reset_url}\n\nEste enlace expira en 24 horas.',
            )
        except Exception as e:
            return Response({'error': f'Error al enviar el email: {str(e)}'}, status=500)

        return Response({'message': 'Si el email existe, recibirÃ¡s un enlace.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not all([uid, token, new_password]):
            return Response({'error': 'Faltan datos'}, status=400)

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = Usuario.objects.get(pk=user_id)
        except (Usuario.DoesNotExist, ValueError):
            return Response({'error': 'Token invÃ¡lido'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Token invÃ¡lido o expirado'}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'ContraseÃ±a actualizada correctamente'})
