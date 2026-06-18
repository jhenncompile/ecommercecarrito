# apps/negocio/recordatorios/api/urls.py
from django.urls import path
from apps.negocio.recordatorios.api.views import RecordatorioViewSet

urlpatterns = [
    # Listado y creación
    path(
        'recordatorios/',
        RecordatorioViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='recordatorio-list',
    ),
    # Detalle, edición y eliminación
    path(
        'recordatorios/<int:pk>/',
        RecordatorioViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='recordatorio-detail',
    ),
    # Marcar como completado (POST) — dispara CU-18
    path(
        'recordatorios/<int:pk>/marcar-completado/',
        RecordatorioViewSet.as_view({'post': 'marcar_completado'}),
        name='recordatorio-marcar-completado',
    ),
    # Próximos 7 días (GET)
    path(
        'recordatorios/proximos/',
        RecordatorioViewSet.as_view({'get': 'proximos'}),
        name='recordatorio-proximos',
    ),
]
