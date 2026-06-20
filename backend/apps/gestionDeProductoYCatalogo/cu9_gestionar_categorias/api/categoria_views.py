from apps.core.views import BaseViewSet
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.api.categoria_serializer import CategoriaSerializer
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.services.categoria_service import CategoriaService


class CategoriaViewSet(BaseViewSet):
    """
    API de Categorías de Productos.
    
    - GET /api/categorias/ - Listar todos
    - POST /api/categorias/ - Crear nuevo
    - GET /api/categorias/{id}/ - Detalle
    - PUT /api/categorias/{id}/ - Actualizar
    - DELETE /api/categorias/{id}/ - Eliminar
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    modulo_auditoria = "Categoria"
    
    def get_queryset(self):
        from django.db import connection
        if connection.schema_name == 'public':
            return Categoria.objects.none()
        return super().get_queryset()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = CategoriaService()
