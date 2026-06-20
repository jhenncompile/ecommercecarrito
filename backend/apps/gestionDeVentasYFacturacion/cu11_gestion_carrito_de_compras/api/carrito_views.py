from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.authentication import ClienteJWTAuthentication, UsuarioJWTAuthentication
from apps.core.views import BaseViewSet
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito import Carrito
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.api.carrito_serializers import CarritoSerializer
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.services.carrito_service import CarritoService
from apps.customers.models import Cliente


class CarritoViewSet(BaseViewSet):
    """
    API de Carritos de Compra.
    
    - GET /api/carritos/ - Listar todos
    - POST /api/carritos/ - Crear nuevo
    - GET /api/carritos/{id}/ - Detalle con items
    - PUT /api/carritos/{id}/ - Actualizar estado
    - DELETE /api/carritos/{id}/ - Eliminar
    
    Acciones especiales:
    - POST /api/carritos/{id}/agregar-item/ - Agregar producto al carrito
    - POST /api/carritos/{id}/eliminar-item/ - Remover producto
    - POST /api/carritos/{id}/vaciar/ - Limpiar todos los items
    - POST /api/carritos/{id}/cerrar/ - Convertir en pedido
    """
    queryset = Carrito.objects.select_related('cliente').prefetch_related('items__producto').all()
    serializer_class = CarritoSerializer
    authentication_classes = [ClienteJWTAuthentication, UsuarioJWTAuthentication]
    modulo_auditoria = "Carrito"
    
    def get_service(self):
        return CarritoService()

    def _cliente_id_autenticado(self):
        auth = getattr(self.request, 'auth', None)
        if hasattr(auth, 'get') and auth.get('role') == 'CLIENTE':
            return auth.get('cliente_id') or auth.get('user_id')
        return None

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        from django.db import connection
        if connection.schema_name == 'public':
            return Carrito.objects.none()
            
        queryset = super().get_queryset()
        cliente_id = self._cliente_id_autenticado()
        if cliente_id:
            return queryset.filter(cliente_id=cliente_id)
        return queryset

    def create(self, request, *args, **kwargs):
        cliente_id = self._cliente_id_autenticado()
        if cliente_id:
            try:
                carrito, created = self.get_service().obtener_o_crear_carrito_abierto(cliente_id)
                serializer = self.get_serializer(carrito)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )
            except Cliente.DoesNotExist:
                return Response({'error': 'El cliente asociado al token no existe.'}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        cliente_id = self._cliente_id_autenticado()
        if cliente_id:
            cliente = Cliente.objects.get(id=cliente_id)
            serializer.save(cliente=cliente)
            return
        super().perform_create(serializer)
    
    @action(detail=True, methods=['post'], url_path='agregar-item')
    def agregar_item(self, request, pk=None):
        """Agrega un producto al carrito."""
        try:
            carrito = self.get_object()
            producto_id = request.data.get('producto_id')
            cantidad = request.data.get('cantidad', 1)
            
            self.get_service().agregar_item(carrito.id, producto_id, cantidad)
            carrito.refresh_from_db()
            serializer = self.get_serializer(carrito)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='eliminar-item')
    def eliminar_item(self, request, pk=None):
        """Elimina un producto del carrito."""
        try:
            carrito = self.get_object()
            producto_id = request.data.get('producto_id')
            
            self.get_service().eliminar_item(carrito.id, producto_id)
            carrito.refresh_from_db()
            serializer = self.get_serializer(carrito)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def vaciar(self, request, pk=None):
        """VacÃ­a todos los items del carrito."""
        carrito = self.get_object()
        self.get_service().vaciar_carrito(carrito.id)
        carrito.refresh_from_db()
        serializer = self.get_serializer(carrito)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        """Cierra el carrito para convertirlo en pedido."""
        carrito = self.get_object()
        self.get_service().cerrar_carrito(carrito.id)
        carrito.refresh_from_db()
        serializer = self.get_serializer(carrito)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

