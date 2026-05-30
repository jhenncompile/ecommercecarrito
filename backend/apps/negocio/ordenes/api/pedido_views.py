from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.views import BaseViewSet
from apps.negocio.models import Pedido
from apps.negocio.ordenes.api.pedido_serializer import PedidoSerializer
from apps.negocio.ordenes.services.pedido_service import PedidoService


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

    def get_queryset(self):
        from django.db import connection
        if connection.schema_name == 'public':
            return Pedido.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            return Pedido.objects.none()
            
        # El token de cliente usa 'role' (ClienteTokenUser) o 'rol' (Usuario)
        user_role = getattr(user, 'role', getattr(user, 'rol', None))
        
        # Si es un cliente, solo ver sus pedidos
        if user_role == 'CLIENTE':
            email = getattr(user, 'email', getattr(user, 'correo', None))
            if email:
                return Pedido.objects.filter(carrito__cliente__correo=email).order_by('-fecha_creacion')
            return Pedido.objects.none()
            
        return Pedido.objects.all().order_by('-fecha_creacion')

    @action(detail=False, methods=['get'], url_path='global-list')
    def global_list(self, request):
        """
        Obtiene los pedidos del cliente logueado a través de todos los tenants.
        """
        from django_tenants.utils import schema_context
        from apps.customers.models import Client
        
        if not request.user.is_authenticated:
            return Response([])
            
        email = getattr(request.user, 'email', getattr(request.user, 'correo', None))
        if not email:
            return Response([])
        import traceback
        
        all_pedidos = []
        try:
            tenants = Client.objects.exclude(schema_name='public')
            for tenant in tenants:
                with schema_context(tenant.schema_name):
                    try:
                        # En tu modelo Cliente, el campo se llama 'correo', no 'email'
                        pedidos = Pedido.objects.filter(carrito__cliente__correo=email)
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
    
    def get_service(self):
        return PedidoService()

    def create(self, request, *args, **kwargs):
        """
        Crea un pedido desde el checkout del cliente.
        Acepta el payload del frontend: {items: [{producto, cantidad, precio_unitario}], total}
        También soporta la creación estándar con carrito_id.
        """
        from apps.customers.models import Cliente

        items = request.data.get('productos') or request.data.get('items')

        if items and isinstance(items, list):
            # Flujo del PublicStorefront: crear carrito + pedido directo
            try:
                # Obtener cliente desde el token JWT de cliente
                email = getattr(request.user, 'email', getattr(request.user, 'correo', None))
                if not email:
                    return Response({'error': 'Cliente no encontrado o no autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)
                cliente = Cliente.objects.get(correo=email)

                # Evitar duplicados: Si hay un PENDIENTE, lo eliminamos para crear uno actualizado
                pedido_existente = Pedido.objects.filter(
                    carrito__cliente=cliente, estado='PENDIENTE'
                ).first()
                if pedido_existente:
                    pedido_existente.carrito.delete()

                pedido = self.get_service().crear_pedido_directo(cliente.id, items)
                serializer = self.get_serializer(pedido)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Cliente.DoesNotExist:
                return Response(
                    {'error': 'Cliente no encontrado. Debes iniciar sesión.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Flujo estándar (admin/vendedor con carrito_id)
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
            
            pedido = self.get_service().crear_pedido_desde_carrito(carrito_id)
            serializer = self.get_serializer(pedido)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado de un pedido."""
        try:
            nuevo_estado = request.data.get('estado')
            if not nuevo_estado:
                return Response(
                    {'error': 'estado es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            pedido = self.get_service().cambiar_estado(pk, nuevo_estado)
            serializer = self.get_serializer(pedido)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
