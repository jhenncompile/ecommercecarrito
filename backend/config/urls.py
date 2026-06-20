from apps.gestionDeUsuarioySeguridad.cu2_cerrar_sesion.api.views import LogoutView
from apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.api.views import MyTokenObtainPairView
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# App Negocio
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.api.views import ProductoViewSet
from apps.gestionDeProductoYCatalogo.cu8_visualizar_listado_de_productos.api.catalogo_views import CatalogoProductoViewSet
from apps.gestionDeProductoYCatalogo.cu10_gestionar_inventario.api.views import InventarioViewSet
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.api.categoria_views import CategoriaViewSet
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.api.carrito_views import CarritoViewSet
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.api.views import PedidoViewSet
from apps.gestionDeVentasYFacturacion.cu15_ver_historial_de_compras.api.historial_views import HistorialComprasViewSet
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.api.views import FacturaViewSet
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.api.tipo_pago_views import TipoPagoViewSet
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.api.pago_views import PagoViewSet

# Customers
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.api.views import (
     UsuarioCrudViewSet,
    PasswordResetRequestView, PasswordResetConfirmView,
    MiPerfilView
)
from apps.customers.api.mobile_views import (
    LatestReleaseInfoView, DownloadLatestReleaseView, DownloadSpecificReleaseView,
    UploadMobileReleaseView
)
from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.api.rol_views import RolViewSet
from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.api.permiso_views import PermisoViewSet
from apps.customers.tenants.api.plan_views import PlanViewSet
from apps.customers.clientes.api.views import ClienteViewSet, ClienteLoginView
from apps.customers.tenants.api.views import TiendaPublicViewSet, TiendaPerfilView, UpgradeSuscripcionView
from apps.gestionDeUsuarioySeguridad.cu6_gestionar_bitacora.api.bitacora_views import BitacoraViewSet
from apps.gestionDeReportes.cu21_generar_backup.api.respaldo_views import RespaldoViewSet
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.api.device_token_views import DeviceTokenRegisterView

# Voice
from apps.voice.api.views import VoiceQueryView, VoiceTaskStatusView
from apps.gestionDeReportes.cu18_gestionar_notificaciones.api.views import NotificacionViewSet

# 1. Configuramos el enrutador de la API
router = DefaultRouter()

# App Negocio
router.register(r'productos', ProductoViewSet, basename='productos')
router.register(r'catalogo', CatalogoProductoViewSet, basename='catalogo')
router.register(r'inventario', InventarioViewSet, basename='inventario')
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'carritos', CarritoViewSet, basename='carritos')
router.register(r'pedidos', PedidoViewSet, basename='pedidos')
router.register(r'historial-compras', HistorialComprasViewSet, basename='historial-compras')
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

    
    path('api/usuarios/perfil/', MiPerfilView.as_view(), name='mi_perfil'),
    path('api/tienda/perfil/', TiendaPerfilView.as_view(), name='tienda_perfil'),
    path('api/tienda/suscripcion/upgrade/', UpgradeSuscripcionView.as_view(), name='suscripcion_upgrade'),

    # Mobile Releases (Public)
    path('api/public/apps/latest/', LatestReleaseInfoView.as_view(), name='apps_latest'),
    path('api/public/apps/<str:app_type>/latest/download/', DownloadLatestReleaseView.as_view(), name='apps_latest_download'),
    path('api/public/apps/<str:app_type>/version/<str:version>/download/', DownloadSpecificReleaseView.as_view(), name='apps_version_download'),
    path('api/public/apps/upload/', UploadMobileReleaseView.as_view(), name='apps_upload'),

    path('api/reportes/', include('apps.gestionDeReportes.cu19_generar_reportes_de_ventas.api.urls')),
    path('api/tiendas/', include('apps.customers.tenants.api.urls')),
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


