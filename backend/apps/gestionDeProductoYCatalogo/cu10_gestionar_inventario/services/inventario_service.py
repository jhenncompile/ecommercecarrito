from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto

class InventarioService:
    @staticmethod
    def anadir_stock(producto_id, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad a aÃ±adir debe ser mayor a cero.")
        
        producto = Producto.objects.get(id=producto_id)
        producto.stock += cantidad
        producto.save()
        return producto

    @staticmethod
    def reducir_stock(producto_id, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad a reducir debe ser mayor a cero.")
        
        producto = Producto.objects.get(id=producto_id)
        if producto.stock < cantidad:
            raise ValueError("Stock insuficiente.")
            
        producto.stock -= cantidad
        producto.save()
        return producto
