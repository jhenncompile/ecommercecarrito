from django.urls import path
from apps.customers.tenants.api.views import (
    TenantListView, TenantCreateView, CheckoutSuscripcionView, CrearTiendaConPagoView
)

urlpatterns = [
    path('', TenantListView.as_view(), name='tenant-list'),
    path('crear/', TenantCreateView.as_view(), name='tenant-create'),
    path('checkout-suscripcion/', CheckoutSuscripcionView.as_view(), name='tenant-checkout-suscripcion'),
    path('crear-con-pago/', CrearTiendaConPagoView.as_view(), name='tenant-crear-con-pago'),
]
