from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.api.views import (
    ReporteConfigViewSet, 
    ReporteEstaticoAPIView, 
    ReportBuilderAPIView,
    ReportMetadataAPIView,
    ExportAPIView
)

router = DefaultRouter()
router.register(r'configuraciones', ReporteConfigViewSet, basename='reporte_config')

urlpatterns = [
    path('estatico/<str:tipo>/', ReporteEstaticoAPIView.as_view(), name='reporte_estatico'),
    path('builder/', ReportBuilderAPIView.as_view(), name='reporte_builder'),
    path('metadata/', ReportMetadataAPIView.as_view(), name='reporte_metadata'),
    path('export/', ExportAPIView.as_view(), name='reporte_export'),
    path('', include(router.urls)),
]
