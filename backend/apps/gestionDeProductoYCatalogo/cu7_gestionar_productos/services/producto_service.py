from apps.core.services import BaseService
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto

class ProductoService(BaseService):
    def __init__(self):
        super().__init__(Producto)