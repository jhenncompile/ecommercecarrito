# apps/customers/tenants/api/urls.py
# Rutas del módulo tenants - incluidas en config/urls.py
from django.urls import path
from apps.customers.views.tenant_views import TiendaPublicViewSet, TiendaPerfilView
from apps.customers.views.plan_views import PlanViewSet

urlpatterns = [
    path('tiendas/', __import__('customers.views.usuario_views', fromlist=['TenantListView']).TenantListView.as_view()),
    path('tiendas/crear/', __import__('customers.views.usuario_views', fromlist=['TenantCreateView']).TenantCreateView.as_view()),
    path('tiendas/checkout-suscripcion/', __import__('customers.views.usuario_views', fromlist=['CheckoutSuscripcionView']).CheckoutSuscripcionView.as_view()),
    path('tiendas/crear-con-pago/', __import__('customers.views.usuario_views', fromlist=['CrearTiendaConPagoView']).CrearTiendaConPagoView.as_view()),
    path('tienda/perfil/', TiendaPerfilView.as_view(), name='tienda_perfil'),
]
