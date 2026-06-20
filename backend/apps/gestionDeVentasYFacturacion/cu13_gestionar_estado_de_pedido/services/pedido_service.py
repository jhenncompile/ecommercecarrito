from apps.core.services import BaseService
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido, Carrito
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
        from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito_item import CarritoItem
        from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
        from apps.customers.clientes.models.cliente import Cliente
        
        with transaction.atomic():
            cliente = Cliente.objects.get(id=cliente_id)
            carrito = Carrito.objects.create(cliente=cliente, estado='CERRADO')
            
            for item in items:
                prod_id = item.get('producto_id') or item.get('producto')
                if not prod_id:
                    raise ValueError("El item no contiene 'producto_id'")
                producto = Producto.objects.select_for_update().get(id=prod_id)
                cantidad_solicitada = int(item['cantidad'])
                
                if producto.stock < cantidad_solicitada:
                    raise ValueError(f"Stock insuficiente para {producto.nombre}. Solicitado: {cantidad_solicitada}, Disponible: {producto.stock}")
                    
                # Descontar el stock
                producto.stock -= cantidad_solicitada
                producto.save()
                
                CarritoItem.objects.create(
                    carrito=carrito,
                    producto=producto,
                    cantidad=cantidad_solicitada
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
        estado_anterior = pedido.estado
        pedido.estado = nuevo_estado
        pedido.save()
        
        # Notificar al cliente si el estado cambia a algo relevante (PROCESADO, ENVIADO, ENTREGADO, CANCELADO)
        if estado_anterior != nuevo_estado and nuevo_estado in ['PROCESADO', 'ENVIADO', 'ENTREGADO', 'CANCELADO']:
            try:
                from apps.gestionDeReportes.cu18_gestionar_notificaciones.services.notification_service import send_notification
                mensajes = {
                    'PROCESADO': 'ha sido procesado y está siendo preparado.',
                    'ENVIADO': 'ha sido enviado y está en camino hacia tu dirección.',
                    'ENTREGADO': 'ha sido entregado con éxito. ¡Gracias por tu compra!',
                    'CANCELADO': 'ha sido cancelado.'
                }
                
                send_notification(
                    cliente=pedido.carrito.cliente,
                    titulo=f"Actualización de Pedido #{pedido.id}",
                    mensaje=f"Tu pedido {mensajes.get(nuevo_estado, 'ha cambiado de estado.')}",
                    tipo="PEDIDO"
                )
            except Exception as e:
                print(f" Error al notificar cambio de estado: {str(e)}")
                
        return pedido
    
    def obtener_por_cliente(self, cliente_id):
        """Obtiene todos los pedidos de un cliente."""
        return Pedido.objects.filter(carrito__cliente_id=cliente_id).order_by('-fecha_creacion')
    
    def obtener_por_estado(self, estado):
        """Obtiene pedidos por estado."""
        return Pedido.objects.filter(estado=estado).order_by('-fecha_creacion')
