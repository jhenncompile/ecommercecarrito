from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.permissions import HasPermiso
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.models.reporte_config import ReporteConfig
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.api.serializers import ReporteConfigSerializer
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.report_service import ReportService
import csv
from django.http import HttpResponse
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.builders import get_report_metadata
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.orchestrator import ExportOrchestrator

class ReportMetadataAPIView(APIView):
    """
    Devuelve la estructura de los modelos disponibles para el Query Builder.
    """
    permission_classes = [HasPermiso]
    required_permiso = 'REP_DINAMICO'

    def get(self, request):
        metadata = get_report_metadata()
        return Response(metadata, status=status.HTTP_200_OK)

class ReporteConfigViewSet(viewsets.ModelViewSet):
    """
    CRUD para configuraciones de reportes guardados por el usuario.
    Solo para planes que tengan permisos de reportes dinámicos.
    """
    queryset = ReporteConfig.objects.all()
    serializer_class = ReporteConfigSerializer
    permission_classes = [HasPermiso]
    required_permiso = 'REP_DINAMICO'

class ReporteEstaticoAPIView(APIView):
    """
    Genera reportes estáticos predefinidos.
    Para el plan básico o superior.
    """
    permission_classes = [HasPermiso]
    required_permiso = 'REP_ESTATICO'

    def get(self, request, tipo):
        try:
            datos = ReportService.generar_estatico(tipo)
            
            # Export to CSV if requested
            if request.query_params.get('format') == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="reporte_{tipo}.csv"'
                
                if not datos:
                    return response
                
                writer = csv.writer(response)
                # Escribir cabeceras
                primer_fila = datos[0]
                writer.writerow(primer_fila.keys())
                
                for fila in datos:
                    writer.writerow(fila.values())
                return response

            return Response(datos, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReportBuilderAPIView(APIView):
    """
    Ejecuta un reporte dinámico basado en un JSON.
    Para el plan medio o superior.
    """
    permission_classes = [HasPermiso]
    required_permiso = 'REP_DINAMICO'

    def post(self, request):
        config = request.data
        if not config:
            return Response({"error": "No se proporcionó configuración."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            datos = ReportService.ejecutar_dinamico(config)
            return Response(datos, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExportAPIView(APIView):
    """
    Endpoint centralizado para orquestar la exportación de reportes (PDF/Excel)
    generados enteramente en el backend.
    """
    permission_classes = [HasPermiso]
    required_permiso = 'REP_ESTATICO' # Requerimos un permiso base, aunque podría ser más granular

    def post(self, request):
        config = request.data
        fmt = config.get('format', 'pdf')
        export_type = config.get('type', 'estatico')
        metadata = config.get('metadata', {})

        if not export_type or not fmt:
            return Response({"error": "Faltan parámetros 'format' o 'type'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Delegate to the orchestrator
            response = ExportOrchestrator.generate(export_type, fmt, metadata)
            return response
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"error": f"Error al generar exportación: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
