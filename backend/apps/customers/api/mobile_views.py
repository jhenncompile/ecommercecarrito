from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
import os
from apps.customers.models.mobile_release import MobileRelease

class LatestReleaseInfoView(APIView):
    """
    Retorna la informacion de la ultima version para cada tipo de app.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        cliente_latest = MobileRelease.objects.filter(app_type='cliente', is_latest=True).first()
        vendedor_latest = MobileRelease.objects.filter(app_type='vendedor', is_latest=True).first()

        data = {
            'cliente': None,
            'vendedor': None
        }

        if cliente_latest:
            data['cliente'] = {
                'version': cliente_latest.version,
                'created_at': cliente_latest.created_at,
                'download_url': f"/api/public/apps/cliente/latest/download/"
            }
        
        if vendedor_latest:
            data['vendedor'] = {
                'version': vendedor_latest.version,
                'created_at': vendedor_latest.created_at,
                'download_url': f"/api/public/apps/vendedor/latest/download/"
            }

        return Response(data)


class DownloadLatestReleaseView(APIView):
    """
    Redirige al archivo APK de la ultima version, provocando su descarga directa.
    """
    permission_classes = [AllowAny]

    def get(self, request, app_type):
        release = get_object_or_404(MobileRelease, app_type=app_type, is_latest=True)
        # Redirigir directamente al archivo fÃ­sico en el storage (MEDIA_URL)
        return redirect(release.file.url)


class DownloadSpecificReleaseView(APIView):
    """
    Redirige al archivo APK de una version especifica.
    Ruta solicitada por el usuario: /app/<app_type>/version/<version>/download
    """
    permission_classes = [AllowAny]

    def get(self, request, app_type, version):
        release = get_object_or_404(MobileRelease, app_type=app_type, version=version)
        return redirect(release.file.url)


class UploadMobileReleaseView(APIView):
    """
    Recibe un archivo APK desde un script y lo guarda en la base de datos.
    Requiere un token secreto en el header X-Upload-Secret.
    """
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        secret = request.headers.get('X-Upload-Secret')
        # Utilizamos un secret que por defecto serÃ¡ 'miqhatu_super_secret_upload_token_2026' si no estÃ¡ en .env
        expected_secret = getattr(settings, 'MOBILE_UPLOAD_SECRET', 'miqhatu_super_secret_upload_token_2026')
        
        if not secret or secret != expected_secret:
            return Response({'error': 'No autorizado. Token invÃ¡lido.'}, status=403)

        app_type = request.data.get('app_type')
        version = request.data.get('version')
        file_obj = request.data.get('file')

        if not app_type or not version or not file_obj:
            return Response({'error': 'Faltan datos requeridos (app_type, version, file).'}, status=400)

        if app_type not in ['cliente', 'vendedor']:
            return Response({'error': 'app_type invÃ¡lido. Debe ser cliente o vendedor.'}, status=400)

        # Crear y guardar la release, y marcarla como la Ãºltima
        release = MobileRelease(
            app_type=app_type,
            version=version,
            file=file_obj,
            is_latest=True
        )
        release.save()

        return Response({
            'message': 'APK subido exitosamente.',
            'app_type': release.app_type,
            'version': release.version,
            'url': release.file.url
        }, status=201)

