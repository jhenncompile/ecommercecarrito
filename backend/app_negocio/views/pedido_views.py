from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.views import BaseViewSet
from app_negocio.models import Pedido
from app_negocio.serializers.pedido_serializer import PedidoSerializer
from app_negocio.services.pedido_service import PedidoService


class PedidoViewSet(BaseViewSet):
    """
    API de Pedidos.
    
    - GET /api/pedidos/ - Listar todos
    - POST /api/pedidos/ - Crear nuevo
    - GET /api/pedidos/{id}/ - Detalle
    - PUT /api/pedidos/{id}/ - Actualizar estado
    - DELETE /api/pedidos/{id}/ - Eliminar
    
    Acciones especiales:
    - POST /api/pedidos/crear-desde-carrito/ - Convertir carrito en pedido
    - POST /api/pedidos/{id}/cambiar-estado/ - Cambiar estado del pedido
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    modulo_auditoria = "Pedido"

    @action(detail=False, methods=['get'], url_path='global-list')
    def global_list(self, request):
        from django_tenants.utils import schema_context
        from customers.models import Client
        import traceback
        
        all_pedidos = []
        try:
            tenants = Client.objects.exclude(schema_name='public')
            for tenant in tenants:
                with schema_context(tenant.schema_name):
                    try:
                        # En tu modelo Cliente, el campo se llama 'correo', no 'email'
                        pedidos = Pedido.objects.filter(carrito__cliente__correo=request.user.email)
                        for p in pedidos:
                            # Forzamos el contexto del serializer para evitar errores de esquema
                            serializer = self.get_serializer(p)
                            data = serializer.data
                            data['tenant_name'] = tenant.name
                            data['schema_name'] = tenant.schema_name
                            all_pedidos.append(data)
                    except Exception as e_tenant:
                        print(f"⚠️ Error en tenant {tenant.schema_name}: {str(e_tenant)}")
            
            return Response(all_pedidos)
        except Exception as e:
            print("❌ ERROR EN BUSQUEDA GLOBAL:")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=500)
        qs = super().get_queryset()
        user = self.request.user
        
        # Si el usuario es un Cliente (Lightweight user de ClienteJWTAuthentication)
        if hasattr(user, 'role') and user.role == "CLIENTE":
            return qs.filter(carrito__cliente_id=user.id)
            
        return qs
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = PedidoService()

    def create(self, request, *args, **kwargs):
        # Evitar duplicados: Si ya hay un pedido PENDIENTE para este usuario, lo reutilizamos
        from customers.models import Cliente
        try:
            # Buscamos por el email del usuario autenticado
            cliente = Cliente.objects.get(correo=request.user.email)
            pedido_existente = Pedido.objects.filter(carrito__cliente=cliente, estado='PENDIENTE').first()
            if pedido_existente:
                serializer = self.get_serializer(pedido_existente)
                return Response(serializer.data)
        except Exception:
            pass
            
        return super().create(request, *args, **kwargs)
        """Sobrescribe la creación para permitir crear pedido directo con items."""
        items = request.data.get('items')
        if items and isinstance(items, list):
            try:
                # El ID del cliente lo sacamos del usuario autenticado
                cliente_id = request.user.id
                pedido = self.service.crear_pedido_directo(cliente_id, items)
                serializer = self.get_serializer(pedido)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def crear_desde_carrito(self, request):
        """Crea un pedido a partir de un carrito abierto."""
        try:
            carrito_id = request.data.get('carrito_id')
            if not carrito_id:
                return Response(
                    {'error': 'carrito_id es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            pedido = self.service.crear_pedido_desde_carrito(carrito_id)
            serializer = self.get_serializer(pedido)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado de un pedido."""
        try:
            nuevo_estado = request.data.get('estado')
            if not nuevo_estado:
                return Response(
                    {'error': 'estado es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            pedido = self.service.cambiar_estado(pk, nuevo_estado)
            serializer = self.get_serializer(pedido)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
