from apps.core.services import BaseService
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria


class CategoriaService(BaseService):
    """Servicio de Categorías de Productos."""
    
    def __init__(self):
        super().__init__(Categoria)
    
    def obtener_activas(self):
        """Obtiene solo categorías activas."""
        return Categoria.objects.filter(activo=True)
    
    def obtener_principales(self):
        """Obtiene solo categorías principales (sin padre)."""
        return Categoria.objects.filter(parent__isnull=True)
    
    def obtener_subcategorias(self, categoria_id):
        """Obtiene subcategorías de una categoría."""
        categoria = self.obtener(categoria_id)
        if categoria:
            return categoria.subcategorias.all()
        return Categoria.objects.none()
    
    def obtener_por_nombre(self, nombre):
        """Obtiene categoría por nombre."""
        return Categoria.objects.filter(nombre=nombre).first()
