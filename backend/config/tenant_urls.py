from apps.gestionDeUsuarioySeguridad.cu2_cerrar_sesion.api.views import LogoutView
from apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.api.views import MyTokenObtainPairView
from django.http import JsonResponse
from django.db import connection
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.api.carrito_views import CarritoViewSet
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.api.views import PedidoViewSet
from apps.gestionDeVentasYFacturacion.cu15_ver_historial_de_compras.api.historial_views import HistorialComprasViewSet
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.api.views import ProductoViewSet
from apps.gestionDeProductoYCatalogo.cu8_visualizar_listado_de_productos.api.catalogo_views import CatalogoProductoViewSet
from apps.gestionDeProductoYCatalogo.cu10_gestionar_inventario.api.views import InventarioViewSet
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.api.categoria_views import CategoriaViewSet
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.api.views import FacturaViewSet
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.api.tipo_pago_views import TipoPagoViewSet
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.api.pago_views import PagoViewSet
from apps.gestionDeReportes.cu18_gestionar_notificaciones.api.views import NotificacionViewSet
from apps.gestionDeReportes.cu20_gestionar_recordatorios.api.views import RecordatorioViewSet
from apps.voice.api.views import VoiceQueryView, VoiceTaskStatusView
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.api.views import (
    UsuarioCrudViewSet,
    PasswordResetRequestView, PasswordResetConfirmView, MiPerfilView
)
from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.api.rol_views import RolViewSet
from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.api.permiso_views import PermisoViewSet
from apps.customers.tenants.api.plan_views import PlanViewSet
from apps.gestionDeClientes.cu17_analizar_comportamiento_del_cliente.api.behavior_views import ComportamientoClientesAPIView
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.api.device_token_views import DeviceTokenRegisterView
from apps.gestionDeReportes.cu21_generar_backup.api.respaldo_views import RespaldoViewSet
from apps.gestionDeUsuarioySeguridad.cu6_gestionar_bitacora.api.bitacora_views import BitacoraViewSet
from apps.customers.tenants.api.views import TiendaPerfilView
from apps.gestionDeClientes.cu22_gestionar_prediccion_de_ventas.api.forecast_views import PrediccionVentasAPIView

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
    path('api/catalogo/', CatalogoProductoViewSet.as_view({'get': 'list'}), name='catalogo-list'),
    path('api/catalogo/<int:pk>/', CatalogoProductoViewSet.as_view({'get': 'retrieve'}), name='catalogo-detail'),
    path('api/catalogo/<int:pk>/recomendaciones/', CatalogoProductoViewSet.as_view({'get': 'recomendaciones'}), name='catalogo-recomendaciones'),
    path('api/inventario/<int:pk>/anadir-stock/', InventarioViewSet.as_view({'post': 'anadir_stock'}), name='inventario-anadir-stock'),
    path('api/inventario/<int:pk>/reducir-stock/', InventarioViewSet.as_view({'post': 'reducir_stock'}), name='inventario-reducir-stock'),
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
    path('api/historial-compras/', HistorialComprasViewSet.as_view({'get': 'list'}), name='historial-compras-list'),
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

    # Usuarios, Roles, Permisos, Planes
    path('api/usuarios/', UsuarioCrudViewSet.as_view({'get': 'list', 'post': 'create'}), name='usuario-list'),
    path('api/usuarios/<int:pk>/', UsuarioCrudViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='usuario-detail'),
    path('api/roles/', RolViewSet.as_view({'get': 'list', 'post': 'create'}), name='rol-list'),
    path('api/roles/<int:pk>/', RolViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='rol-detail'),
    path('api/permisos/', PermisoViewSet.as_view({'get': 'list', 'post': 'create'}), name='permiso-list'),
    path('api/permisos/<int:pk>/', PermisoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='permiso-detail'),
    path('api/planes/', PlanViewSet.as_view({'get': 'list'}), name='plan-list'),
    path('api/planes/<int:pk>/', PlanViewSet.as_view({'get': 'retrieve'}), name='plan-detail'),

    # Perfil del usuario autenticado
    path('api/usuarios/perfil/', MiPerfilView.as_view(), name='mi_perfil'),
    path('api/tienda/perfil/', TiendaPerfilView.as_view(), name='tienda_perfil'),

    # Consultas por voz
    path('api/vquery/', VoiceQueryView.as_view(), name='voice_query'),
    path('api/vquery/status/<uuid:task_id>/', VoiceTaskStatusView.as_view(), name='voice_task_status'),

    # Notificaciones
    path('api/notificaciones/', NotificacionViewSet.as_view({'get': 'list', 'put': 'update', 'patch': 'partial_update'}), name='notificacion-list'),
    path('api/notificaciones/marcar-todas-leidas/', NotificacionViewSet.as_view({'post': 'marcar_todas_leidas'}), name='notificacion-marcar-todas'),

    # Reportes
    path('api/reportes/comportamiento-clientes/', ComportamientoClientesAPIView.as_view(), name='comportamiento_clientes'),
    path('api/reportes/prediccion/', PrediccionVentasAPIView.as_view(), name='prediccion_ventas'),
    path('api/reportes/', include('apps.gestionDeReportes.cu19_generar_reportes_de_ventas.api.urls')),

    # Recordatorios (CU-20)
    path('api/recordatorios/', RecordatorioViewSet.as_view({'get': 'list', 'post': 'create'}), name='recordatorio-list'),
    path('api/recordatorios/proximos/', RecordatorioViewSet.as_view({'get': 'proximos'}), name='recordatorio-proximos'),
    path('api/recordatorios/<int:pk>/', RecordatorioViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='recordatorio-detail'),
    path('api/recordatorios/<int:pk>/marcar-completado/', RecordatorioViewSet.as_view({'post': 'marcar_completado'}), name='recordatorio-marcar-completado'),

    # Bitacora (CU-6)
    path('api/bitacora/', BitacoraViewSet.as_view({'get': 'list'}), name='bitacora-list'),
    path('api/bitacora/<int:pk>/', BitacoraViewSet.as_view({'get': 'retrieve'}), name='bitacora-detail'),

    # Respaldos (CU-21)
    path('api/respaldos/', RespaldoViewSet.as_view({'get': 'list', 'post': 'create'}), name='respaldos-list'),
    path('api/respaldos/config/', RespaldoViewSet.as_view({'get': 'config', 'post': 'config'}), name='respaldos-config'),
    path('api/respaldos/historial/', RespaldoViewSet.as_view({'get': 'historial_encadenado'}), name='respaldos-historial-encadenado'),
    path('api/respaldos/<int:pk>/', RespaldoViewSet.as_view({'get': 'retrieve'}), name='respaldos-detail'),
    path('api/respaldos/<int:pk>/restaurar/', RespaldoViewSet.as_view({'post': 'restaurar'}), name='respaldos-restaurar'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


