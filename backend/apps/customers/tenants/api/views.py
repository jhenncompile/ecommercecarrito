from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from apps.customers.models import Client
from apps.customers.tenants.api.serializers import TiendaPublicSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser


class DirectorioPagination(PageNumberPagination):
    """
    Paginación personalizada para el directorio de tiendas.
    Muestra 12 tiendas por página para la grilla del frontend.
    """
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class TiendaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint público para listar y buscar tiendas en el Marketplace (Escenario C).
    
    Características:
    - Solo tiendas activas
    - Acceso público sin autenticación (AllowAny)
    - Optimización de consultas con prefetch_related
    - Paginación de 12 tiendas por página
    - Filtrado por categoría
    - Búsqueda de texto libre en nombre y descripción
    
    Endpoints:
    - GET /api/tiendas-publicas/ - Listar tiendas públicas (paginado)
    - GET /api/tiendas-publicas/?search=boutique - Buscar por texto
    - GET /api/tiendas-publicas/?categoria_tienda=ropa - Filtrar por categoría
    """
    
    # Solo tiendas activas
    queryset = Client.objects.filter(activo=True).prefetch_related('domains')
    serializer_class = TiendaPublicSerializer
    permission_classes = [AllowAny]  # Acceso sin JWT
    pagination_class = DirectorioPagination
    
    # Filtros y búsqueda
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria_tienda']  # Permite filtrado exacto por categoría
    search_fields = ['nombre_comercial', 'descripcion']  # Búsqueda por texto libre
    ordering_fields = ['nombre_comercial', 'created_on']
    ordering = ['nombre_comercial']  # Ordenamiento por defecto — evita UnorderedObjectListWarning


class TiendaPerfilView(APIView):
    """
    Endpoint para que el vendedor administre los datos de su propia tienda.
    Devuelve métricas privadas como plan activo y límites.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        tenant = request.tenant
        from apps.customers.tenants.api.serializers import TiendaPrivadaSerializer
        serializer = TiendaPrivadaSerializer(tenant, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        tenant = request.tenant
        
        # Manually parse the data to allow updating icono
        if 'nombre_comercial' in request.data:
            tenant.nombre_comercial = request.data['nombre_comercial']
        if 'descripcion' in request.data:
            tenant.descripcion = request.data['descripcion']
        if 'categoria_tienda' in request.data:
            tenant.categoria_tienda = request.data['categoria_tienda']
        if 'icono' in request.FILES:
            tenant.icono = request.FILES['icono']
            
        tenant.save()
        from apps.customers.tenants.api.serializers import TiendaPrivadaSerializer
        serializer = TiendaPrivadaSerializer(tenant, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpgradeSuscripcionView(APIView):
    """
    Endpoint para que un tenant existente inicie o pague un upgrade de suscripción.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        payment_intent_id = request.data.get('payment_intent')
        tenant = request.tenant

        from apps.customers.tenants.models.plan import Plan
        try:
            nuevo_plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response({'error': 'Plan no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        import stripe
        from django.conf import settings
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Caso 1: Inicializar el intento de pago (devuelve clientSecret)
        if not payment_intent_id:
            try:
                # Precio en centavos
                amount = int(nuevo_plan.precio_mensual * 100)
                
                # Si el plan es gratuito, no cobramos
                if amount == 0:
                    tenant.plan = nuevo_plan
                    tenant.save()
                    return Response({'success': True, 'message': 'Plan actualizado a Gratuito.'}, status=status.HTTP_200_OK)

                intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency='usd',
                    automatic_payment_methods={'enabled': True},
                    metadata={'tenant_schema': tenant.schema_name, 'nuevo_plan_id': nuevo_plan.id}
                )
                return Response({'clientSecret': intent.client_secret}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Caso 2: Confirmar el pago exitoso y aplicar el plan
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status != 'succeeded':
                return Response({'error': 'El pago no fue exitoso.'}, status=status.HTTP_400_BAD_REQUEST)
                
            tenant.plan = nuevo_plan
            from apps.customers.tenants.services.billing_helper import BillingDateHelper
            fecha_inicio, fecha_fin = BillingDateHelper.calcular_fechas_mensuales()
            
            tenant.fecha_inicio_suscripcion = fecha_inicio
            tenant.fecha_fin_suscripcion = fecha_fin
            tenant.save()
            
            return Response({'success': True, 'message': f'Plan actualizado a {nuevo_plan.nombre}'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
