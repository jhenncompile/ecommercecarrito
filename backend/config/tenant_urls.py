from django.http import JsonResponse
from django.db import connection
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from app_negocio.views.carrito_views import CarritoViewSet
from app_negocio.views.producto_views import ProductoViewSet
from app_negocio.views.categoria_views import CategoriaViewSet
from app_negocio.views.pedido_views import PedidoViewSet
from app_negocio.views.factura_views import FacturaViewSet, TipoPagoViewSet
from app_negocio.views.pago_views import PagoViewSet
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

    # Carritos para sincronización post-SSO de clientes
    path('api/carritos/', CarritoViewSet.as_view({'get': 'list', 'post': 'create'}), name='carrito-list'),
    path('api/carritos/<int:pk>/', CarritoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='carrito-detail'),
    path('api/carritos/<int:pk>/agregar-item/', CarritoViewSet.as_view({'post': 'agregar_item'}), name='carrito-agregar-item'),
    path('api/carritos/<int:pk>/eliminar-item/', CarritoViewSet.as_view({'post': 'eliminar_item'}), name='carrito-eliminar-item'),
    path('api/carritos/<int:pk>/vaciar/', CarritoViewSet.as_view({'post': 'vaciar'}), name='carrito-vaciar'),
    path('api/carritos/<int:pk>/cerrar/', CarritoViewSet.as_view({'post': 'cerrar'}), name='carrito-cerrar'),

    # Password Reset (también en tenants para facilitar acceso)
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Pedidos
    path('api/pedidos/', PedidoViewSet.as_view({'get': 'list', 'post': 'create'}), name='pedido-list'),
    path('api/pedidos/<int:pk>/', PedidoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='pedido-detail'),
    path('api/pedidos/crear-desde-carrito/', PedidoViewSet.as_view({'post': 'crear_desde_carrito'}), name='pedido-desde-carrito'),
    path('api/pedidos/<int:pk>/cambiar-estado/', PedidoViewSet.as_view({'post': 'cambiar_estado'}), name='pedido-cambiar-estado'),

    # Pagos y Facturas
    path('api/facturas/', FacturaViewSet.as_view({'get': 'list', 'post': 'create'}), name='factura-list'),
    path('api/pagos/', PagoViewSet.as_view({'get': 'list', 'post': 'create'}), name='pago-list'),
    path('api/pagos/create-checkout-session/', PagoViewSet.as_view({'post': 'create_checkout_session'}), name='pago-stripe-session'),

    # Categorías
    path('api/categorias/', CategoriaViewSet.as_view({'get': 'list', 'post': 'create'}), name='categoria-list'),

    # Perfil del usuario autenticado
    path('api/usuarios/perfil/', MiPerfilView.as_view(), name='mi_perfil'),

    # Consultas por voz
    path('api/vquery/', VoiceQueryView.as_view(), name='voice_query'),
]
