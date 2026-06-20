# apps/negocio/recordatorios/api/views.py
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.gestionDeReportes.cu20_gestionar_recordatorios.models.recordatorio import Recordatorio
from apps.gestionDeReportes.cu20_gestionar_recordatorios.api.serializers import RecordatorioSerializer


class RecordatorioViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de recordatorios del usuario autenticado.

    Endpoints adicionales:
      POST  /recordatorios/<pk>/marcar-completado/   → marca completado y envía notificación (CU-18)
      GET   /recordatorios/proximos/                 → recordatorios pendientes próximos 7 días
    """

    serializer_class = RecordatorioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Recordatorio.objects.none()

        qs = Recordatorio.objects.filter(usuario=user)

        # Filtros opcionales via query params
        tipo = self.request.query_params.get('tipo')
        completado = self.request.query_params.get('completado')

        if tipo:
            qs = qs.filter(tipo=tipo.upper())
        if completado is not None:
            val = completado.lower() in ('true', '1', 'yes')
            qs = qs.filter(completado=val)

        return qs

    def perform_create(self, serializer):
        """Asigna el usuario autenticado al crear el recordatorio."""
        recordatorio = serializer.save(usuario=self.request.user)
        # CU-18: Enviar notificación in-app al crear el recordatorio
        self._enviar_notificacion_creacion(recordatorio)

    def _enviar_notificacion_creacion(self, recordatorio):
        """Dispara la notificación CU-18 al guardar un recordatorio."""
        try:
            from apps.gestionDeReportes.cu18_gestionar_notificaciones.services.notification_service import send_notification
            tipo_labels = {'TAREA': '📋 Tarea', 'PAGO': '💳 Pago', 'PROMOCION': '🏷️ Promoción'}
            label = tipo_labels.get(recordatorio.tipo, recordatorio.tipo)
            send_notification(
                usuario=recordatorio.usuario,
                titulo=f"Recordatorio creado: {recordatorio.titulo}",
                mensaje=(
                    f"{label} programado para el "
                    f"{recordatorio.fecha_recordatorio:%d/%m/%Y a las %H:%M}."
                ),
                tipo='SISTEMA',
            )
        except Exception as e:
            print(f"⚠️ No se pudo enviar notificación de recordatorio: {e}")

    @action(detail=True, methods=['post'], url_path='marcar-completado')
    def marcar_completado(self, request, pk=None):
        """
        POST /api/recordatorios/<pk>/marcar-completado/
        Marca el recordatorio como completado y envía notificación (CU-18).
        """
        recordatorio = self.get_object()
        if recordatorio.completado:
            return Response(
                {'detail': 'El recordatorio ya está completado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recordatorio.completado = True
        recordatorio.notificacion_enviada = True
        recordatorio.save()

        # CU-18: Notificar que fue completado
        try:
            from apps.gestionDeReportes.cu18_gestionar_notificaciones.services.notification_service import send_notification
            send_notification(
                usuario=recordatorio.usuario,
                titulo=f"✅ Recordatorio completado: {recordatorio.titulo}",
                mensaje=f"Has marcado el recordatorio '{recordatorio.titulo}' como completado.",
                tipo='SISTEMA',
            )
        except Exception as e:
            print(f"⚠️ Error al notificar completado: {e}")

        serializer = self.get_serializer(recordatorio)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='proximos')
    def proximos(self, request):
        """
        GET /api/recordatorios/proximos/
        Retorna los recordatorios pendientes de los próximos 7 días.
        """
        ahora = timezone.now()
        en_7_dias = ahora + timedelta(days=7)
        qs = self.get_queryset().filter(
            completado=False,
            fecha_recordatorio__gte=ahora,
            fecha_recordatorio__lte=en_7_dias,
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
