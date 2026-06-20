from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import TruncMonth, TruncYear
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.customers.clientes.models.cliente import Cliente
from .registry import ReportRegistry

ESTADOS_VENTA_COBRADA = ['PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO']

@ReportRegistry.register_estatico('ventas_mensuales', 'Ventas Mensuales')
def ventas_mensuales():
    return Pedido.objects.filter(estado__in=ESTADOS_VENTA_COBRADA).annotate(
        mes=TruncMonth('fecha_creacion')
    ).values('mes').annotate(
        total_ventas=Sum(
            F('carrito__items__producto__precio') * F('carrito__items__cantidad'),
            output_field=DecimalField()
        ),
        cantidad_pedidos=Count('id', distinct=True)
    ).order_by('-mes')[:12]

@ReportRegistry.register_estatico('ventas_anuales', 'Ventas Anuales')
def ventas_anuales():
    return Pedido.objects.filter(estado__in=ESTADOS_VENTA_COBRADA).annotate(
        año=TruncYear('fecha_creacion')
    ).values('año').annotate(
        total_ventas=Sum(
            F('carrito__items__producto__precio') * F('carrito__items__cantidad'),
            output_field=DecimalField()
        ),
        cantidad_pedidos=Count('id', distinct=True)
    ).order_by('-año')[:5]

@ReportRegistry.register_estatico('top_productos', 'Top Productos por Stock')
def top_productos():
    return Producto.objects.filter(activo=True).order_by('-stock')[:10].values('id', 'nombre', 'stock', 'precio')

@ReportRegistry.register_estatico('top_categorias', 'Top Categorías por Cantidad de Productos')
def top_categorias():
    return Categoria.objects.filter(activo=True).annotate(
        cantidad_productos=Count('productos')
    ).order_by('-cantidad_productos')[:10].values('id', 'nombre', 'cantidad_productos')

@ReportRegistry.register_estatico('nuevos_clientes', 'Nuevos Clientes por Mes')
def nuevos_clientes():
    return Cliente.objects.annotate(
        mes=TruncMonth('fecha_registro')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('-mes')[:12]

@ReportRegistry.register_estatico('nuevos_clientes_anual', 'Nuevos Clientes por Año')
def nuevos_clientes_anual():
    return Cliente.objects.annotate(
        año=TruncYear('fecha_registro')
    ).values('año').annotate(
        total=Count('id')
    ).order_by('-año')[:5]
