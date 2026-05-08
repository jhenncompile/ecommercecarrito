from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from app_negocio.views.producto_views import ProductoViewSet
from app_negocio.views.categoria_views import CategoriaViewSet
from app_negocio.views.carrito_views import CarritoViewSet
from app_negocio.views.pedido_views import PedidoViewSet
from app_negocio.views.factura_views import FacturaViewSet, TipoPagoViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from customers.views.usuario_views import (
    MyTokenObtainPairView, LogoutView, UsuarioCrudViewSet,
    PasswordResetRequestView, PasswordResetConfirmView,
    TenantListView, TenantCreateView, MiPerfilView
)
from customers.views.rol_views import RolViewSet
from customers.views.plan_views import PlanViewSet
from customers.views.cliente_views import ClienteViewSet, ClienteLoginView
from customers.views.tenant_views import TiendaPublicViewSet

# 1. Configuramos el enrutador de la API
router = DefaultRouter()

# App Negocio
router.register(r'productos', ProductoViewSet, basename='productos')
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'carritos', CarritoViewSet, basename='carritos')
router.register(r'pedidos', PedidoViewSet, basename='pedidos')
router.register(r'facturas', FacturaViewSet, basename='facturas')
router.register(r'tipos-pago', TipoPagoViewSet, basename='tipos-pago')

# Customers
router.register(r'usuarios', UsuarioCrudViewSet, basename='usuarios')
router.register(r'roles', RolViewSet, basename='roles')
router.register(r'planes', PlanViewSet, basename='planes')
router.register(r'clientes', ClienteViewSet, basename='clientes')

# Escenario C: Marketplace Público
router.register(r'tiendas-publicas', TiendaPublicViewSet, basename='tiendas-publicas')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 2. Rutas para autenticación JWT
    # Login Administrativo (Ya existente)
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # NUEVO: Login exclusivo para Clientes (Customers)
    path('api/clientes/login/', ClienteLoginView.as_view(), name='cliente_login'),

    path('api/tiendas/', TenantListView.as_view()),
    path('api/tiendas/crear/', TenantCreateView.as_view()),
    
    # 3.5. RUTA DE PERFIL DEL USUARIO AUTENTICADO
    path('api/usuarios/perfil/', MiPerfilView.as_view(), name='mi_perfil'),

    # 3. Incluimos las rutas de nuestra API de negocio (Productos)
    path('api/', include(router.urls)),

    # 4. Rutas de Documentación (drf-spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]