from django.http import JsonResponse
from django.db import connection
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from apps.negocio.ordenes.api.views import CarritoViewSet
from apps.negocio.ordenes.api.pedido_views import PedidoViewSet
from apps.negocio.catalogo.api.views import ProductoViewSet
from apps.negocio.catalogo.api.categoria_views import CategoriaViewSet
from apps.negocio.billing.api.views import FacturaViewSet, TipoPagoViewSet
from apps.negocio.billing.api.pago_views import PagoViewSet
from apps.negocio.notificaciones.api.views import NotificacionViewSet
from apps.negocio.recordatorios.api.views import RecordatorioViewSet
from apps.voice.api.views import VoiceQueryView, VoiceTaskStatusView
from apps.customers.users.api.views import (
    MyTokenObtainPairView, LogoutView,
    PasswordResetRequestView, PasswordResetConfirmView, MiPerfilView
)
from apps.customers.users.api.device_token_views import DeviceTokenRegisterView

def debug_schema(request):
    return JsonResponse({'urlconf': 'config.tenant_urls', 'schema': connection.schema_name})

urlpatterns = [
    path('api/debug/', debug_schema),

    # Auth
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    
    path('api/device-token/', DeviceTokenRegisterView.as_view(), name='device_token_register'),

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
    path('api/facturas/<str:nro>/descargar_pdf/', FacturaViewSet.as_view({'get': 'descargar_pdf'}), name='factura-pdf'),
    path('api/tipos-pago/', TipoPagoViewSet.as_view({'get': 'list', 'post': 'create'}), name='tipo-pago-list'),
    
    path('api/pagos/', PagoViewSet.as_view({'get': 'list', 'post': 'create'}), name='pago-list'),
    path('api/pagos/create-checkout-session/', PagoViewSet.as_view({'post': 'create_checkout_session'}), name='pago-stripe-session'),
    path('api/pagos/webhook/', PagoViewSet.as_view({'post': 'stripe_webhook'}), name='pago-stripe-webhook'),
    path('api/pagos/confirm-success/', PagoViewSet.as_view({'post': 'confirm_success'}), name='pago-confirm-success'),

    # Categorías
    path('api/categorias/', CategoriaViewSet.as_view({'get': 'list', 'post': 'create'}), name='categoria-list'),

    # Perfil del usuario autenticado
    path('api/usuarios/perfil/', MiPerfilView.as_view(), name='mi_perfil'),

    # Consultas por voz
    path('api/vquery/', VoiceQueryView.as_view(), name='voice_query'),
    path('api/vquery/status/<uuid:task_id>/', VoiceTaskStatusView.as_view(), name='voice_task_status'),

    # Notificaciones
    path('api/notificaciones/', NotificacionViewSet.as_view({'get': 'list', 'put': 'update', 'patch': 'partial_update'}), name='notificacion-list'),
    path('api/notificaciones/marcar-todas-leidas/', NotificacionViewSet.as_view({'post': 'marcar_todas_leidas'}), name='notificacion-marcar-todas'),

    # Reportes
    path('api/reportes/', include('apps.negocio.reportes.api.urls')),

    # Recordatorios (CU-20)
    path('api/recordatorios/', RecordatorioViewSet.as_view({'get': 'list', 'post': 'create'}), name='recordatorio-list'),
    path('api/recordatorios/proximos/', RecordatorioViewSet.as_view({'get': 'proximos'}), name='recordatorio-proximos'),
    path('api/recordatorios/<int:pk>/', RecordatorioViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='recordatorio-detail'),
    path('api/recordatorios/<int:pk>/marcar-completado/', RecordatorioViewSet.as_view({'post': 'marcar_completado'}), name='recordatorio-marcar-completado'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


