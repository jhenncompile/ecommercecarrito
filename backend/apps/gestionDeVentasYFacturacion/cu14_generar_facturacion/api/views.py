from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.views import BaseViewSet
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.factura import Factura, TipoPago
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.api.serializers import FacturaSerializer, TipoPagoSerializer
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.services.factura_service import FacturaService, TipoPagoService


class FacturaViewSet(BaseViewSet):
    """
    API de Facturas.
    
    - GET /api/facturas/ - Listar todas
    - POST /api/facturas/ - Crear nueva
    - GET /api/facturas/{nro}/ - Detalle (por nÃºmero de factura)
    - PUT /api/facturas/{nro}/ - Actualizar
    - DELETE /api/facturas/{nro}/ - Eliminar
    
    Acciones especiales:
    - POST /api/facturas/crear-desde-pedido/ - Generar factura desde pedido
    - POST /api/facturas/{nro}/anular/ - Anular factura
    """
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    modulo_auditoria = "Factura"
    lookup_field = 'nro'

    def get_queryset(self):
        from django.db import connection
        if connection.schema_name == 'public':
            return Factura.objects.none()
            
        queryset = Factura.objects.all()
        pedido_id = self.request.query_params.get('pedido')
        if pedido_id:
            queryset = queryset.filter(pedido_id=pedido_id)
        return queryset
    
    def list(self, request, *args, **kwargs):
        from django.db import connection
        from django_tenants.utils import schema_context
        from apps.customers.models import Client
        
        if connection.schema_name == 'public':
            pedido_id = request.query_params.get('pedido')
            if pedido_id:
                tenants = Client.objects.exclude(schema_name='public')
                for tenant in tenants:
                    with schema_context(tenant.schema_name):
                        facturas = Factura.objects.filter(pedido_id=pedido_id)
                        if facturas.exists():
                            serializer = self.get_serializer(facturas, many=True)
                            return Response(serializer.data)
            return Response([])
            
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        from django.db import connection
        from django_tenants.utils import schema_context
        from apps.customers.models import Client
        from django.http import Http404
        
        nro = self.kwargs.get('nro')
        if connection.schema_name == 'public' and nro:
            tenants = Client.objects.exclude(schema_name='public')
            for tenant in tenants:
                with schema_context(tenant.schema_name):
                    try:
                        factura = Factura.objects.get(nro=nro)
                        serializer = self.get_serializer(factura)
                        return Response(serializer.data)
                    except Factura.DoesNotExist:
                        continue
            raise Http404("Factura no encontrada")
            
        return super().retrieve(request, *args, **kwargs)

    def get_service(self):
        return FacturaService()
    
    @action(detail=False, methods=['post'])
    def crear_desde_pedido(self, request):
        """Crea una factura a partir de un pedido."""
        try:
            pedido_id = request.data.get('pedido_id')
            tipo_pago_id = request.data.get('tipo_pago_id')
            
            if not pedido_id:
                return Response(
                    {'error': 'pedido_id es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            factura = self.get_service().crear_factura_desde_pedido(pedido_id, tipo_pago_id)
            serializer = self.get_serializer(factura)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def descargar_pdf(self, request, nro=None):
        """Genera y descarga el PDF de la factura."""
        from django.db import connection
        from django_tenants.utils import schema_context
        from apps.customers.models import Client
        from django.http import Http404, FileResponse
        from apps.negocio.billing.utils.pdf_generator import generar_pdf_factura
        
        try:
            if connection.schema_name == 'public':
                tenants = Client.objects.exclude(schema_name='public')
                for tenant in tenants:
                    with schema_context(tenant.schema_name):
                        try:
                            factura = Factura.objects.get(nro=nro)
                            pdf_buffer = generar_pdf_factura(factura)
                            return FileResponse(
                                pdf_buffer, 
                                as_attachment=True, 
                                filename=f"factura_{factura.nro}.pdf"
                            )
                        except Factura.DoesNotExist:
                            continue
                raise Http404("Factura no encontrada")
            else:
                factura = self.get_object()
                pdf_buffer = generar_pdf_factura(factura)
                
                return FileResponse(
                    pdf_buffer, 
                    as_attachment=True, 
                    filename=f"factura_{factura.nro}.pdf"
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def anular(self, request, nro=None):
        """Anula una factura."""
        try:
            factura = self.get_service().anular_factura(nro)
            serializer = self.get_serializer(factura)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

