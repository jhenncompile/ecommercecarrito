from django.http import JsonResponse
from django.db import connection
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from app_negocio.views.producto_views import ProductoViewSet
from voice_query.views.query_view import VoiceQueryView
from customers.views.usuario_views import (
    MyTokenObtainPairView, LogoutView,
    PasswordResetRequestView, PasswordResetConfirmView, MiPerfilView
)

# Debug temporal
def debug_schema(request):
    return JsonResponse({'urlconf': 'config.tenant_urls', 'schema': connection.schema_name})

# URLs explícitas SIN usar DefaultRouter para evitar conflictos de nombre con config.urls
urlpatterns = [
    path('api/debug/', debug_schema),

    # Auth
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),

    # Productos - paths explícitos, sin DefaultRouter
    path('api/productos/', ProductoViewSet.as_view({'get': 'list', 'post': 'create'}), name='producto-list'),
    path('api/productos/<int:pk>/', ProductoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='producto-detail'),

    # Password Reset (también en tenants para facilitar acceso)
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Perfil del usuario autenticado
    path('api/usuarios/perfil/', MiPerfilView.as_view(), name='mi_perfil'),

    # Consultas por voz
    path('api/vquery/', VoiceQueryView.as_view(), name='voice_query'),
]
