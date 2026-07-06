from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from apps.customers.models import Client
from apps.customers.tenants.api.serializers import TiendaPublicSerializer, TenantCreateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings


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
    
    serializer_class = TiendaPublicSerializer
    permission_classes = [AllowAny]  # Acceso sin JWT
    pagination_class = DirectorioPagination
    
    def get_queryset(self):
        from django.utils import timezone
        today = timezone.now().date()
        return Client.objects.filter(activo=True).exclude(limite_alcanzado_fecha=today).prefetch_related('domains')
    
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
        if 'ciudad' in request.data:
            tenant.ciudad = request.data['ciudad']
        if 'whatsapp' in request.data:
            tenant.whatsapp = request.data['whatsapp']
        if 'enable_local_delivery' in request.data:
            tenant.enable_local_delivery = str(request.data['enable_local_delivery']).lower() in ('true', '1', 'on', 'yes')
        if 'enable_national_shipping' in request.data:
            tenant.enable_national_shipping = str(request.data['enable_national_shipping']).lower() in ('true', '1', 'on', 'yes')
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
                    
                    # Sincronizar permisos
                    from django_tenants.utils import tenant_context
                    from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.models.rol import Rol
                    from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.models.permiso import Permiso
                    with tenant_context(tenant):
                        permisos_basicos = list(Permiso.objects.filter(es_basico=True))
                        nuevos_permisos = list(nuevo_plan.permisos.all())
                        permisos_totales = permisos_basicos + nuevos_permisos
                        
                        rol_admin = Rol.objects.filter(nombre__iexact='administrador').first()
                        if rol_admin:
                            rol_admin.permisos.set(permisos_totales)
                        rol_vendedor = Rol.objects.filter(nombre__iexact='vendedor').first()
                        if rol_vendedor:
                            rol_vendedor.permisos.set(permisos_totales)

                    return Response({'success': True, 'message': 'Plan actualizado a Gratuito.'}, status=status.HTTP_200_OK)

                if not stripe.api_key:
                    return Response({'error': 'Configuración de Stripe incompleta'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency='usd',
                    automatic_payment_methods={'enabled': True},
                    metadata={'tenant_schema': tenant.schema_name, 'nuevo_plan_id': nuevo_plan.id}
                )
                # Se usa settings global
                return Response({
                    'clientSecret': intent.client_secret,
                    'publishableKey': settings.STRIPE_PUBLISHABLE_KEY
                }, status=status.HTTP_200_OK)
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
            
            # Sincronizar permisos en los roles locales del tenant
            from django_tenants.utils import tenant_context
            from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.models.rol import Rol
            from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.models.permiso import Permiso
            with tenant_context(tenant):
                permisos_basicos = list(Permiso.objects.filter(es_basico=True))
                nuevos_permisos = list(nuevo_plan.permisos.all())
                permisos_totales = permisos_basicos + nuevos_permisos
                
                # Reasignar la totalidad de permisos (básicos + premium del nuevo plan)
                rol_admin = Rol.objects.filter(nombre__iexact='administrador').first()
                if rol_admin:
                    rol_admin.permisos.set(permisos_totales)
                    
                rol_vendedor = Rol.objects.filter(nombre__iexact='vendedor').first()
                if rol_vendedor:
                    rol_vendedor.permisos.set(permisos_totales)
            
            return Response({'success': True, 'message': f'Plan actualizado a {nuevo_plan.nombre}'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TenantCreateView(APIView):
    """Creación de nuevos esquemas (tiendas) - Plan Gratuito."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TenantCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Asignar plan básico por defecto si no viene o viene 'basico'
            plan_code = request.data.get('plan', 'basico')
            from apps.customers.tenants.models.plan import Plan
            try:
                plan = Plan.objects.get(nombre__iexact=plan_code)
            except Plan.DoesNotExist:
                plan = Plan.objects.filter(precio_mensual=0).first()
            
            result = serializer.save(plan=plan)
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckoutSuscripcionView(APIView):
    """Inicializa un PaymentIntent de Stripe para un Plan."""
    permission_classes = [AllowAny]

    def post(self, request):
        plan_code = request.data.get('plan')
        if not plan_code or plan_code == 'basico':
            return Response({'error': 'Plan inválido para pago'}, status=status.HTTP_400_BAD_REQUEST)
            
        from apps.customers.tenants.models.plan import Plan
        try:
            plan = Plan.objects.get(nombre__iexact=plan_code)
        except Plan.DoesNotExist:
            return Response({'error': 'Plan no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            # Precio en centavos
            amount = int(plan.precio_mensual * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                automatic_payment_methods={'enabled': True},
                metadata={'plan_id': plan.id, 'nombre_tienda': request.data.get('nombre_tienda', '')}
            )
            # Se usa settings global
            return Response({
                'clientSecret': intent.client_secret,
                'publishableKey': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrearTiendaConPagoView(APIView):
    """Crea la tienda tras validar el pago exitoso en Stripe."""
    permission_classes = [AllowAny]

    def post(self, request):
        payment_intent_id = request.data.get('payment_intent')
        if not payment_intent_id:
            return Response({'error': 'Falta el ID del pago'}, status=status.HTTP_400_BAD_REQUEST)

        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status != 'succeeded':
                return Response({'error': 'El pago no fue exitoso.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Proceder a crear el tenant
        serializer = TenantCreateSerializer(data=request.data)
        if serializer.is_valid():
            plan_code = request.data.get('plan', 'profesional')
            from apps.customers.tenants.models.plan import Plan
            try:
                plan = Plan.objects.get(nombre__iexact=plan_code)
            except Plan.DoesNotExist:
                plan = None

            # Asignar fechas de suscripción si pagó
            from apps.customers.tenants.services.billing_helper import BillingDateHelper
            fecha_inicio, fecha_fin = BillingDateHelper.calcular_fechas_mensuales()

            result = serializer.save(plan=plan, fecha_inicio_suscripcion=fecha_inicio, fecha_fin_suscripcion=fecha_fin)
            return Response(result, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantListView(APIView):
    """Listado público de tiendas registradas."""
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.customers.tenants.models.tenant import Client
        from apps.customers.tenants.api.serializers import TiendaPublicSerializer
        tenants = Client.objects.exclude(schema_name='public')
        serializer = TiendaPublicSerializer(tenants, many=True, context={'request': request})
        return Response(serializer.data)


# --- Utilidades y Recuperacion de Contraseña ---

def send_email_ssl(to_email, subject, body):
    from django.core.mail import send_mail
    send_mail(subject, body, settings.EMAIL_HOST_USER, [to_email], fail_silently=False)

