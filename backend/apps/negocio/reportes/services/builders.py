from django.db.models import Sum, Count, F, Q, DecimalField
from django.db.models.functions import TruncMonth, TruncDay
from apps.negocio.ordenes.models.pedido import Pedido
from apps.negocio.catalogo.models.producto import Producto
from .registry import ReportRegistry

class ModelReportBuilder:
    """
    Clase base para construir consultas de reportes dinámicos usando el ORM de Django.
    """
    model = None
    metricas = {}         # Diccionario de { 'nombre_metrica': expression }
    agrupaciones = {}     # Diccionario de { 'nombre_agrupacion': expression }
    filtros_permitidos = [] # Lista de nombres de campos que se pueden filtrar

    def __init__(self, config):
        self.metrica = config.get('metrica', 'conteo')
        self.agrupar_por = config.get('agrupar_por')
        self.filtros = config.get('filtros', {})

    def build(self):
        if not self.model:
            raise NotImplementedError("El builder debe especificar un 'model'.")
            
        qs = self.model.objects.all()
        
        # 1. Aplicar Filtros
        for k, v in self.filtros.items():
            if k in self.filtros_permitidos:
                qs = qs.filter(**{k: v})
        
        # 2. Aplicar Agrupación
        if self.agrupar_por in self.agrupaciones:
            qs = qs.annotate(grupo=self.agrupaciones[self.agrupar_por])
        else:
            qs = qs.annotate(grupo=F('id')) # Por defecto (sin agrupación)
            
        qs = qs.values('grupo')
        
        # 3. Aplicar Métrica
        if self.metrica in self.metricas:
            qs = qs.annotate(resultado=self.metricas[self.metrica])
        else:
            # Fallback seguro
            qs = qs.annotate(resultado=Count('id'))
            
        return qs.order_by('-grupo')


@ReportRegistry.register_dinamico('pedidos', 'Pedidos y Ventas')
class PedidoReportBuilder(ModelReportBuilder):
    model = Pedido
    metricas = {
        'total': Sum(F('carrito__items__producto__precio') * F('carrito__items__cantidad'), output_field=DecimalField()),
        'conteo': Count('id')
    }
    agrupaciones = {
        'mes': TruncMonth('fecha_creacion'),
        'dia': TruncDay('fecha_creacion'),
        'estado': F('estado')
    }
    filtros_permitidos = ['estado']


@ReportRegistry.register_dinamico('productos', 'Inventario de Productos')
class ProductoReportBuilder(ModelReportBuilder):
    model = Producto
    metricas = {
        'stock': Sum('stock'),
        'conteo': Count('id')
    }
    agrupaciones = {
        'categoria': F('categoria__nombre')
    }
    filtros_permitidos = ['activo']
