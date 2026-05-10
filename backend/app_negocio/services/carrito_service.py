from core.services import BaseService
from app_negocio.models import Carrito, CarritoItem, Producto
from django.db import transaction


class CarritoService(BaseService):
    """Servicio de Carritos de Compra."""
    
    def __init__(self):
        super().__init__(Carrito)
    
    def obtener_carrito_abierto(self, cliente_id):
        """Obtiene el carrito abierto de un cliente (o lo crea)."""
        carrito, _ = self.obtener_o_crear_carrito_abierto(cliente_id)
        return carrito

    def obtener_o_crear_carrito_abierto(self, cliente_id):
        """Obtiene el carrito abierto de un cliente indicando si fue creado."""
        from customers.models.cliente import Cliente
        cliente = Cliente.objects.get(id=cliente_id)
        carrito = (
            Carrito.objects
            .filter(cliente=cliente, estado='ABIERTO')
            .order_by('-fecha_creacion')
            .first()
        )
        if carrito:
            return carrito, False

        carrito = Carrito.objects.create(cliente=cliente, estado='ABIERTO')
        created = True
        return carrito, created
    
    @transaction.atomic
    def agregar_item(self, carrito_id, producto_id, cantidad=1):
        """Agrega un producto al carrito."""
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            raise ValueError("La cantidad debe ser un número entero.")

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")

        carrito = self.obtener(carrito_id)
        producto = Producto.objects.get(id=producto_id)

        # Agregar o actualizar item
        item, created = CarritoItem.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': cantidad}
        )

        nueva_cantidad = cantidad if created else item.cantidad + cantidad

        # Validar stock disponible contra la cantidad total del item
        if producto.stock < nueva_cantidad:
            if created:
                item.delete()
            raise ValueError(f"Stock insuficiente. Disponible: {producto.stock}")
        
        if not created:
            item.cantidad = nueva_cantidad
            item.save()
        
        return item
    
    @transaction.atomic
    def eliminar_item(self, carrito_id, producto_id):
        """Elimina un producto del carrito."""
        CarritoItem.objects.filter(
            carrito_id=carrito_id,
            producto_id=producto_id
        ).delete()
    
    def vaciar_carrito(self, carrito_id):
        """Vacía todos los items del carrito."""
        CarritoItem.objects.filter(carrito_id=carrito_id).delete()
    
    @transaction.atomic
    def cerrar_carrito(self, carrito_id):
        """Cierra un carrito para convertirlo en pedido."""
        carrito = self.obtener(carrito_id)
        carrito.estado = 'CERRADO'
        carrito.save()
        return carrito
