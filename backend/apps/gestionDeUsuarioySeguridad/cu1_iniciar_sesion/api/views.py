from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.api.serializers import MyTokenObtainPairSerializer
from apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.services.auth_service import get_auth_extra_data
from apps.gestionDeUsuarioySeguridad.cu6_gestionar_bitacora.services.bitacora_service import BitacoraService

class MyTokenObtainPairView(APIView):
    """Vista para el inicio de sesión con JWT."""
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = MyTokenObtainPairSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response_data = serializer.validated_data
        extra_data = get_auth_extra_data(serializer.user, request)
        response_data.update(extra_data)

        # Registro manual de acceso (Especial para Login)
        BitacoraService.registrar_acceso(request, serializer.user, "LOGIN")

        return Response(response_data, status=status.HTTP_200_OK)
