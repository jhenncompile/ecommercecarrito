from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import HasPermiso
from apps.customers.audit.services.bitacora_service import BitacoraService
from apps.negocio.reportes.api.serializers import ForecastRequestSerializer
from apps.negocio.reportes.services.forecast_service import ForecastService
from apps.negocio.reportes.utils.excel_generator import generar_excel_prediccion


class PrediccionVentasAPIView(APIView):
    permission_classes = [HasPermiso]
    required_permiso = 'REP_DINAMICO'

    def post(self, request):
        serializer = ForecastRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        config = serializer.validated_data

        errores = ForecastService.validar_configuracion(config)
        if errores:
            return Response(
                {'error': 'Configuración inválida', 'detalles': errores},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            resultado = ForecastService.generar_prediccion(config, usuario=request.user)
            BitacoraService.registrar_accion(
                request.user,
                'Reportes',
                'GENERAR_PREDICCION_VENTAS',
                metadatos={
                    'tipo': resultado.get('tipo'),
                    'granularidad': resultado.get('granularidad'),
                    'cache_key': resultado.get('cache_key'),
                },
                request=request,
            )
            return Response(resultado, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PrediccionVentasExcelAPIView(APIView):
    permission_classes = [HasPermiso]
    required_permiso = 'REP_DINAMICO'

    def post(self, request):
        datos = request.data
        if 'predicciones' not in datos:
            serializer = ForecastRequestSerializer(data=datos)
            serializer.is_valid(raise_exception=True)
            datos = ForecastService.generar_prediccion(serializer.validated_data, usuario=request.user)

        archivo = generar_excel_prediccion(datos)
        filename = f"prediccion_ventas_{timezone.now().date()}.xlsx"
        return FileResponse(
            archivo,
            as_attachment=True,
            filename=filename,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )


class PrediccionProductosAPIView(APIView):
    permission_classes = [HasPermiso]
    required_permiso = 'REP_DINAMICO'

    def get(self, request):
        return Response(ForecastService.listar_productos(), status=status.HTTP_200_OK)


class PrediccionCategoriasAPIView(APIView):
    permission_classes = [HasPermiso]
    required_permiso = 'REP_DINAMICO'

    def get(self, request):
        return Response(ForecastService.listar_categorias(), status=status.HTTP_200_OK)
