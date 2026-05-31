from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import TruncMonth
from apps.negocio.ordenes.models.pedido import Pedido
from apps.negocio.catalogo.models.producto import Producto
from apps.customers.clientes.models.cliente import Cliente
from .registry import ReportRegistry

@ReportRegistry.register_estatico('ventas_mensuales', 'Ventas Mensuales')
def ventas_mensuales():
    return Pedido.objects.filter(estado='COMPLETADO').annotate(
        mes=TruncMonth('fecha_creacion')
    ).values('mes').annotate(
        total_ventas=Sum(
            F('carrito__items__producto__precio') * F('carrito__items__cantidad'),
            output_field=DecimalField()
        ),
        cantidad_pedidos=Count('id')
    ).order_by('-mes')[:12]

@ReportRegistry.register_estatico('top_productos', 'Top Productos por Stock')
def top_productos():
    return Producto.objects.filter(activo=True).order_by('-stock')[:10].values('id', 'nombre', 'stock', 'precio')

@ReportRegistry.register_estatico('nuevos_clientes', 'Nuevos Clientes por Mes')
def nuevos_clientes():
    return Cliente.objects.annotate(
        mes=TruncMonth('creado_en')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('-mes')[:12]
