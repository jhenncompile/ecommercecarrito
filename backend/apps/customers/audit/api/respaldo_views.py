from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.views import BaseViewSet
from ..models.respaldo import RespaldoSistema
from .respaldo_serializer import RespaldoSerializer
from ..services.respaldo_service import RespaldoService

class RespaldoViewSet(BaseViewSet):
    """
    API para gestiÃ³n de Respaldos con Versionado Encadenado.
    """
    queryset = RespaldoSistema.objects.all()
    serializer_class = RespaldoSerializer
    modulo_auditoria = "Respaldo"

    def get_service(self):
        return RespaldoService()

    def create(self, request, *args, **kwargs):
        """Sobrescribe el POST para ejecutar la creaciÃ³n real del backup"""
        nombre = request.data.get('nombre', 'Respaldo Manual')
        try:
            respaldo = self.get_service().crear_respaldo(nombre)
            serializer = self.get_serializer(respaldo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            return Response({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='historial')
    def historial_encadenado(self, request):
        """Retorna el historial con la lÃ³gica de cola y siguiente"""
        try:
            respaldos = self.get_service().obtener_historial_encadenado()
            serializer = self.get_serializer(respaldos, many=True)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            return Response({
                'error': str(e),
                'traceback': traceback.format_exc(),
                'view': 'RespaldoViewSet.historial_encadenado'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get', 'post'], url_path='config')
    def config(self, request):
        """Obtiene o actualiza la configuración de respaldos automáticos"""
        from apps.customers.audit.models.respaldo import ConfiguracionRespaldo
        from django.db import OperationalError, ProgrammingError

        try:
            config_obj, created = ConfiguracionRespaldo.objects.get_or_create(
                id=1, defaults={'hora_ejecucion': '00:00:00'}
            )
        except (OperationalError, ProgrammingError):
            # La tabla aún no existe (migración pendiente) — devolver valores por defecto
            if request.method == 'GET':
                return Response({
                    'activo': False,
                    'frecuencia': 'DIARIO',
                    'hora_ejecucion': '00:00:00',
                    'dia_referencia': 0,
                    '_warning': 'Migración pendiente: ejecuta python manage.py migrate en el VPS'
                })
            return Response({'error': 'Tabla de configuración no existe. Ejecuta las migraciones.'}, status=500)

        if request.method == 'GET':
            return Response({
                'activo': config_obj.activo,
                'frecuencia': config_obj.frecuencia,
                'hora_ejecucion': str(config_obj.hora_ejecucion),
                'dia_referencia': config_obj.dia_referencia
            })

        elif request.method == 'POST':
            config_obj.activo = request.data.get('activo', config_obj.activo)
            config_obj.frecuencia = request.data.get('frecuencia', config_obj.frecuencia)
            config_obj.hora_ejecucion = request.data.get('hora_ejecucion', config_obj.hora_ejecucion)
            config_obj.dia_referencia = request.data.get('dia_referencia', config_obj.dia_referencia)
            config_obj.save()
            return Response({'message': 'Configuración actualizada'})


    @action(detail=True, methods=['post'], url_path='restaurar')
    def restaurar(self, request, pk=None):
        """Restaura el sistema a partir de este respaldo"""
        try:
            self.get_service().restaurar_respaldo(pk)
            return Response({'message': 'Restauración completada con éxito.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

