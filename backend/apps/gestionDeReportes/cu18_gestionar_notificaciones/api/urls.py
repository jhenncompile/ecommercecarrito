# apps/negocio/notificaciones/api/urls.py
from django.urls import path
from app_negocio.views.notificacion_views import NotificacionViewSet

urlpatterns = [
    path('notificaciones/', NotificacionViewSet.as_view({'get': 'list', 'put': 'update', 'patch': 'partial_update'}), name='notificacion-list'),
    path('notificaciones/marcar-todas-leidas/', NotificacionViewSet.as_view({'post': 'marcar_todas_leidas'}), name='notificacion-marcar-todas'),
]
