from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.negocio.reportes.api.views import (
    ReporteConfigViewSet, 
    ReporteEstaticoAPIView, 
    ReportBuilderAPIView,
    ReportMetadataAPIView,
    ExportAPIView
)
from apps.negocio.reportes.api.forecast_views import (
    PrediccionCategoriasAPIView,
    PrediccionProductosAPIView,
    PrediccionVentasAPIView,
    PrediccionVentasExcelAPIView,
)
from apps.negocio.reportes.api.behavior_views import ComportamientoClientesAPIView

router = DefaultRouter()
router.register(r'configuraciones', ReporteConfigViewSet, basename='reporte_config')

urlpatterns = [
    path('estatico/<str:tipo>/', ReporteEstaticoAPIView.as_view(), name='reporte_estatico'),
    path('builder/', ReportBuilderAPIView.as_view(), name='reporte_builder'),
    path('metadata/', ReportMetadataAPIView.as_view(), name='reporte_metadata'),
    path('export/', ExportAPIView.as_view(), name='reporte_export'),
    path('prediccion/', PrediccionVentasAPIView.as_view(), name='prediccion_ventas'),
    path('prediccion/export-excel/', PrediccionVentasExcelAPIView.as_view(), name='prediccion_ventas_excel'),
    path('prediccion/productos/', PrediccionProductosAPIView.as_view(), name='prediccion_productos'),
    path('prediccion/categorias/', PrediccionCategoriasAPIView.as_view(), name='prediccion_categorias'),
    path('comportamiento-clientes/', ComportamientoClientesAPIView.as_view(), name='comportamiento_clientes'),
    path('', include(router.urls)),
]
