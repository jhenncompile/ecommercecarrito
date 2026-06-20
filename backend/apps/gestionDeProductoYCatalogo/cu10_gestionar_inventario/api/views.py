from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
from apps.gestionDeProductoYCatalogo.cu10_gestionar_inventario.services.inventario_service import InventarioService

class InventarioViewSet(viewsets.ViewSet):
    """
    Endpoints especÃ­ficos para manejar el stock sin actualizar todo el producto.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='anadir-stock')
    def anadir_stock(self, request, pk=None):
        cantidad = request.data.get('cantidad')
        if cantidad is None:
            return Response({'error': 'Cantidad es requerida.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cantidad = int(cantidad)
            producto = InventarioService.anadir_stock(pk, cantidad)
            return Response({'mensaje': 'Stock aÃ±adido.', 'stock_actual': producto.stock})
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reducir-stock')
    def reducir_stock(self, request, pk=None):
        cantidad = request.data.get('cantidad')
        if cantidad is None:
            return Response({'error': 'Cantidad es requerida.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cantidad = int(cantidad)
            producto = InventarioService.reducir_stock(pk, cantidad)
            return Response({'mensaje': 'Stock reducido.', 'stock_actual': producto.stock})
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
