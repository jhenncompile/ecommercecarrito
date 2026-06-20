from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.permissions import HasPermiso
from apps.gestionDeClientes.cu17_analizar_comportamiento_del_cliente.services.behavior_service import CustomerBehaviorService

class ComportamientoClientesAPIView(APIView):
    """
    Endpoint para obtener análisis estadístico de comportamiento del cliente:
    - Tasa de repetición
    - K-Means segmentación (RFM)
    - Reglas de asociación (Apriori)
    - Preferencias por categorías
    """
    permission_classes = [HasPermiso]
    required_permiso = 'REP_ESTATICO'

    def get(self, request):
        try:
            datos = CustomerBehaviorService.obtener_analisis_comportamiento()
            return Response(datos, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response(
                {"error": f"Error al analizar el comportamiento de clientes: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
