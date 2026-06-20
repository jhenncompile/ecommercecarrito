from apps.gestionDeUsuarioySeguridad.cu2_cerrar_sesion.api.views import LogoutView
from apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.api.views import MyTokenObtainPairView
# apps/customers/users/api/urls.py
# Rutas del módulo users
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.api.views import (
     UsuarioCrudViewSet,
    PasswordResetRequestView, PasswordResetConfirmView, MiPerfilView,
)
from apps.customers.views.rol_views import RolViewSet
from apps.customers.views.permiso_views import PermisoViewSet
from apps.customers.views.device_token_views import DeviceTokenRegisterView

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('usuarios/perfil/', MiPerfilView.as_view(), name='mi_perfil'),
    path('device-token/', DeviceTokenRegisterView.as_view(), name='device_token_register'),
    path('usuarios/', UsuarioCrudViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('usuarios/<int:pk>/', UsuarioCrudViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('roles/', RolViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('roles/<int:pk>/', RolViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('permisos/', PermisoViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('permisos/<int:pk>/', PermisoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]
