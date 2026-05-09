from core.services import BaseService
from app_negocio.models import Pedido, Carrito
from django.db import transaction


class PedidoService(BaseService):
    """Servicio de Pedidos."""
    
    def __init__(self):
        super().__init__(Pedido)
    
    def crear_pedido_desde_carrito(self, carrito_id):
        """Crea un pedido a partir de un carrito abierto."""
        carrito = Carrito.objects.get(id=carrito_id)
        
        if carrito.estado != 'ABIERTO':
            raise ValueError(f"El carrito debe estar ABIERTO. Estado actual: {carrito.estado}")
        
        if carrito.cantidad_items == 0:
            raise ValueError("No se puede crear un pedido de un carrito vacío")
        
        # Crear pedido
        pedido = Pedido.objects.create(
            carrito=carrito,
            estado='PENDIENTE'
        )
        
        # Cerrar carrito
        carrito.estado = 'CERRADO'
        carrito.save()
        
        return pedido

    def crear_pedido_directo(self, cliente_id, items):
        """Crea un carrito y un pedido en un solo paso."""
        from app_negocio.models import CarritoItem, Producto
        from customers.models import Cliente
        
        with transaction.atomic():
            cliente = Cliente.objects.get(id=cliente_id)
            carrito = Carrito.objects.create(cliente=cliente, estado='CERRADO')
            
            for item in items:
                producto = Producto.objects.get(id=item['producto'])
                CarritoItem.objects.create(
                    carrito=carrito,
                    producto=producto,
                    cantidad=item['cantidad']
                )
            
            pedido = Pedido.objects.create(
                carrito=carrito,
                estado='PENDIENTE'
            )
            return pedido

    def cambiar_estado(self, pedido_id, nuevo_estado):
        """Cambia el estado de un pedido."""
        estados_validos = ['PENDIENTE', 'PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO', 'CANCELADO']
        
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado inválido. Válidos: {estados_validos}")
        
        pedido = self.obtener(pedido_id)
        pedido.estado = nuevo_estado
        pedido.save()
        return pedido
    
    def obtener_por_cliente(self, cliente_id):
        """Obtiene todos los pedidos de un cliente."""
        return Pedido.objects.filter(carrito__cliente_id=cliente_id).order_by('-fecha_creacion')
    
    def obtener_por_estado(self, estado):
        """Obtiene pedidos por estado."""
        return Pedido.objects.filter(estado=estado).order_by('-fecha_creacion')
