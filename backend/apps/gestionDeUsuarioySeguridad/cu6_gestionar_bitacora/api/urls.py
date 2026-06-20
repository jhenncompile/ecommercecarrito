# apps/customers/audit/api/urls.py
from django.urls import path
from apps.customers.views.bitacora_views import BitacoraViewSet
from apps.customers.views.respaldo_views import RespaldoViewSet

urlpatterns = [
    path('bitacora/', BitacoraViewSet.as_view({'get': 'list'}), name='bitacora-list'),
    path('bitacora/<int:pk>/', BitacoraViewSet.as_view({'get': 'retrieve'})),
    path('respaldos/', RespaldoViewSet.as_view({'get': 'list', 'post': 'create'}), name='respaldo-list'),
    path('respaldos/<int:pk>/', RespaldoViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})),
]
