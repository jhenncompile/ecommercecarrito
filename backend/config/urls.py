from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# App Negocio
from apps.negocio.catalogo.api.views import ProductoViewSet
from apps.negocio.catalogo.api.categoria_views import CategoriaViewSet
from apps.negocio.ordenes.api.views import CarritoViewSet
from apps.negocio.ordenes.api.pedido_views import PedidoViewSet
from apps.negocio.billing.api.views import FacturaViewSet, TipoPagoViewSet
from apps.negocio.billing.api.pago_views import PagoViewSet

# Customers
from apps.customers.users.api.views import (
    MyTokenObtainPairView, LogoutView, UsuarioCrudViewSet,
    PasswordResetRequestView, PasswordResetConfirmView,
    TenantListView, TenantCreateView, MiPerfilView,
    CheckoutSuscripcionView, CrearTiendaConPagoView
)
from apps.customers.users.api.rol_views import RolViewSet
from apps.customers.users.api.permiso_views import PermisoViewSet
from apps.customers.tenants.api.plan_views import PlanViewSet
from apps.customers.clientes.api.views import ClienteViewSet, ClienteLoginView
from apps.customers.tenants.api.views import TiendaPublicViewSet, TiendaPerfilView, UpgradeSuscripcionView
from apps.customers.audit.api.bitacora_views import BitacoraViewSet
from apps.customers.audit.api.respaldo_views import RespaldoViewSet
from apps.customers.users.api.device_token_views import DeviceTokenRegisterView

# Voice
from apps.voice.api.views import VoiceQueryView, VoiceTaskStatusView
from apps.negocio.notificaciones.api.views import NotificacionViewSet

# 1. Configuramos el enrutador de la API
router = DefaultRouter()

# App Negocio
router.register(r'productos', ProductoViewSet, basename='productos')
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'carritos', CarritoViewSet, basename='carritos')
router.register(r'pedidos', PedidoViewSet, basename='pedidos')
router.register(r'facturas', FacturaViewSet, basename='facturas')
router.register(r'tipos-pago', TipoPagoViewSet, basename='tipos-pago')
router.register(r'pagos', PagoViewSet, basename='pagos')
router.register(r'notificaciones', NotificacionViewSet, basename='notificaciones')

# Customers
router.register(r'usuarios', UsuarioCrudViewSet, basename='usuarios')
router.register(r'roles', RolViewSet, basename='roles')
router.register(r'permisos', PermisoViewSet, basename='permisos')
router.register(r'planes', PlanViewSet, basename='planes')
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'bitacora', BitacoraViewSet, basename='bitacora')
router.register(r'respaldos', RespaldoViewSet, basename='respaldos')

# Escenario C: Marketplace Público
router.register(r'tiendas-publicas', TiendaPublicViewSet, basename='tiendas-publicas')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 2. Rutas para autenticación JWT
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('api/token/refresh/', from_jwt := __import__('rest_framework_simplejwt.views', fromlist=['TokenRefreshView']).TokenRefreshView.as_view(), name='token_refresh'), 
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    path('api/clientes/login/', ClienteLoginView.as_view(), name='cliente_login'),
    path('api/device-token/', DeviceTokenRegisterView.as_view(), name='device_token_register'),

    path('api/tiendas/', TenantListView.as_view()),
    path('api/tiendas/crear/', TenantCreateView.as_view()),
    path('api/tiendas/checkout-suscripcion/', CheckoutSuscripcionView.as_view()),
    path('api/tiendas/crear-con-pago/', CrearTiendaConPagoView.as_view()),
    
    path('api/usuarios/perfil/', MiPerfilView.as_view(), name='mi_perfil'),
    path('api/tienda/perfil/', TiendaPerfilView.as_view(), name='tienda_perfil'),
    path('api/tienda/suscripcion/upgrade/', UpgradeSuscripcionView.as_view(), name='suscripcion_upgrade'),

    path('api/', include(router.urls)),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/vquery/', VoiceQueryView.as_view(), name='voice_query_public'),
    path('api/vquery/status/<uuid:task_id>/', VoiceTaskStatusView.as_view(), name='voice_task_status_public'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


