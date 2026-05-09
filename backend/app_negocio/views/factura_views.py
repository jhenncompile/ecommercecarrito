from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.views import BaseViewSet
from app_negocio.models import Factura, TipoPago
from app_negocio.serializers.factura_serializer import FacturaSerializer, TipoPagoSerializer
from app_negocio.services.factura_service import FacturaService, TipoPagoService


class TipoPagoViewSet(BaseViewSet):
    """
    API de Tipos de Pago.
    
    - GET /api/tipos-pago/ - Listar todos
    - POST /api/tipos-pago/ - Crear nuevo
    - GET /api/tipos-pago/{id}/ - Detalle
    - PUT /api/tipos-pago/{id}/ - Actualizar
    - DELETE /api/tipos-pago/{id}/ - Eliminar
    """
    queryset = TipoPago.objects.all()
    serializer_class = TipoPagoSerializer
    modulo_auditoria = "TipoPago"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = TipoPagoService()


class FacturaViewSet(BaseViewSet):
    """
    API de Facturas.
    
    - GET /api/facturas/ - Listar todas
    - POST /api/facturas/ - Crear nueva
    - GET /api/facturas/{nro}/ - Detalle (por número de factura)
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
        from django_tenants.utils import schema_context
        from customers.models import Client
        
        qs = Factura.objects.all()
        pedido_id = self.request.query_params.get('pedido')
        
        # Si estamos en public y buscamos por pedido, rastreamos todas las tiendas
        if connection.schema_name == 'public' and pedido_id:
            tenants = Client.objects.exclude(schema_name='public')
            for tenant in tenants:
                with schema_context(tenant.schema_name):
                    factura = Factura.objects.filter(pedido_id=pedido_id).first()
                    if factura:
                        return Factura.objects.filter(id=factura.id)
        
        return qs
    
    def get_object(self):
        from django.db import connection
        from django_tenants.utils import schema_context
        from customers.models import Client
        
        nro = self.kwargs.get('nro')
        if connection.schema_name == 'public' and nro:
            tenants = Client.objects.exclude(schema_name='public')
            for tenant in tenants:
                with schema_context(tenant.schema_name):
                    try:
                        return Factura.objects.get(nro=nro)
                    except Factura.DoesNotExist:
                        continue
        return super().get_object()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = FacturaService()
    
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
            
            factura = self.service.crear_factura_desde_pedido(pedido_id, tipo_pago_id)
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
        try:
            from django.http import FileResponse
            from ..utils.pdf_generator import generar_pdf_factura
            
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
            factura = self.service.anular_factura(nro)
            serializer = self.get_serializer(factura)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
