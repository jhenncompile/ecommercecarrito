from django.db.models import Sum, Count, F, DecimalField, Value, CharField, Q
from django.db.models.functions import TruncYear, TruncMonth, TruncDay
from apps.negocio.ordenes.models.pedido import Pedido
from apps.negocio.catalogo.models.producto import Producto
from apps.customers.clientes.models.cliente import Cliente
from apps.negocio.billing.models.factura import Factura
from .registry import ReportRegistry

ESTADOS_VENTA_COBRADA = ['PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO']

def get_report_metadata():
    return {
        "modelos": [
            {
                "id": "pedidos",
                "nombre": "Ventas y Pedidos",
                "campos": [
                    {"id": "id", "nombre": "Código de Pedido", "tipo": "number"},
                    {"id": "fecha_creacion", "nombre": "Fecha de Creación", "tipo": "date"},
                    {"id": "estado", "nombre": "Estado", "tipo": "string", "opciones": ["PENDIENTE", "PAGADO", "ENVIADO", "ENTREGADO", "CANCELADO"]},
                    {"id": "total_calculado", "nombre": "Total Calculado", "tipo": "number", "is_virtual": True}
                ],
                "metricas": [
                    {"id": "total", "nombre": "Suma Total ($)", "tipo": "sum"},
                    {"id": "conteo", "nombre": "Cantidad de Pedidos", "tipo": "count"}
                ],
                "agrupaciones": [
                    {"id": "año", "nombre": "Año"},
                    {"id": "mes", "nombre": "Mes"},
                    {"id": "dia", "nombre": "Día"},
                    {"id": "estado", "nombre": "Estado"}
                ]
            },
            {
                "id": "productos",
                "nombre": "Inventario de Productos",
                "campos": [
                    {"id": "id", "nombre": "SKU / Código Producto", "tipo": "number"},
                    {"id": "nombre", "nombre": "Nombre", "tipo": "string"},
                    {"id": "stock", "nombre": "Stock", "tipo": "number"},
                    {"id": "precio", "nombre": "Precio", "tipo": "number"},
                    {"id": "activo", "nombre": "Activo", "tipo": "boolean"},
                    {"id": "categoria__nombre", "nombre": "Categoría", "tipo": "string"}
                ],
                "metricas": [
                    {"id": "stock", "nombre": "Suma de Stock", "tipo": "sum"},
                    {"id": "conteo", "nombre": "Cantidad de Productos", "tipo": "count"}
                ],
                "agrupaciones": [
                    {"id": "categoria", "nombre": "Categoría"},
                    {"id": "activo", "nombre": "Activo (Sí/No)"}
                ]
            },
            {
                "id": "clientes",
                "nombre": "Clientes Registrados",
                "campos": [
                    {"id": "id", "nombre": "Código Cliente", "tipo": "number"},
                    {"id": "usuario__first_name", "nombre": "Nombre", "tipo": "string"},
                    {"id": "fecha_registro", "nombre": "Fecha de Registro", "tipo": "date"}
                ],
                "metricas": [
                    {"id": "conteo", "nombre": "Cantidad de Clientes", "tipo": "count"}
                ],
                "agrupaciones": [
                    {"id": "año", "nombre": "Año de Registro"},
                    {"id": "mes", "nombre": "Mes de Registro"}
                ]
            },
            {
                "id": "facturas",
                "nombre": "Facturación y Pagos",
                "campos": [
                    {"id": "nro", "nombre": "Número Factura", "tipo": "string"},
                    {"id": "fecha", "nombre": "Fecha de Emisión", "tipo": "date"},
                    {"id": "estado", "nombre": "Estado", "tipo": "string", "opciones": ["VIGENTE", "ANULADA"]},
                    {"id": "monto_total", "nombre": "Monto Total", "tipo": "number"}
                ],
                "metricas": [
                    {"id": "total", "nombre": "Suma Total ($)", "tipo": "sum"},
                    {"id": "conteo", "nombre": "Cantidad de Facturas", "tipo": "count"}
                ],
                "agrupaciones": [
                    {"id": "año", "nombre": "Año"},
                    {"id": "mes", "nombre": "Mes"},
                    {"id": "estado", "nombre": "Estado"}
                ]
            }
        ],
        "operadores": {
            "string": [
                {"id": "exact", "nombre": "Es igual a"},
                {"id": "icontains", "nombre": "Contiene"},
                {"id": "in", "nombre": "Está en (separado por comas)"}
            ],
            "number": [
                {"id": "exact", "nombre": "Es igual a"},
                {"id": "gt", "nombre": "Mayor que"},
                {"id": "lt", "nombre": "Menor que"},
                {"id": "gte", "nombre": "Mayor o igual que"},
                {"id": "lte", "nombre": "Menor o igual que"}
            ],
            "date": [
                {"id": "exact", "nombre": "En fecha exacta"},
                {"id": "gte", "nombre": "Desde"},
                {"id": "lte", "nombre": "Hasta"}
            ],
            "boolean": [
                {"id": "exact", "nombre": "Es igual a"}
            ]
        }
    }


class ModelReportBuilder:
    """
    Constructor dinámico avanzado que soporta filtros complejos,
    selección dinámica y compatibilidad hacia atrás.
    Mantenemos el nombre ModelReportBuilder para no romper dependencias,
    pero internamente es la versión 'Advanced'.
    """
    model = None
    metricas = {}         # Diccionario de { 'nombre_metrica': expression }
    agrupaciones = {}     # Diccionario de { 'nombre_agrupacion': expression }
    filtros_permitidos = [] # Lista de campos permitidos

    def __init__(self, config):
        self.config = config
        self.tipo_reporte = config.get('tipo_reporte', 'grafico')
        self.metrica = config.get('metrica', 'conteo')
        self.agrupar_por = config.get('agrupar_por')
        self.filtros = config.get('filtros', {})

    def build(self):
        if not self.model:
            raise NotImplementedError("El builder debe especificar un 'model'.")
            
        qs = self.get_queryset()
        
        # 1. Aplicar Filtros Complejos o Simples
        qs = self.apply_filters(qs)
        
        # 2. Según el Tipo de Reporte
        if self.tipo_reporte == 'tabla':
            select_fields = self.config.get('select', [])
            if select_fields:
                valid_selects = [f for f in select_fields if f != 'total_calculado']
                return qs.values(*valid_selects)[:100]
            else:
                return qs.values()[:100]
                
        # MODO GRÁFICO (o predeterminado con agrupacion)
        if self.agrupar_por in (None, '', 'ninguno'):
            qs = qs.annotate(grupo=Value('Total', output_field=CharField()))
        elif self.agrupar_por in self.agrupaciones:
            qs = qs.annotate(grupo=self.agrupaciones[self.agrupar_por])
        else:
            raise ValueError(f"Agrupación no soportada: {self.agrupar_por}")
            
        qs = qs.values('grupo')
        
        # 3. Aplicar Métrica
        if self.metrica in self.metricas:
            qs = qs.annotate(resultado=self.metricas[self.metrica])
        else:
            raise ValueError(f"Métrica no soportada: {self.metrica}")
            
        ordenar_por = self.config.get('ordenar_por', '-grupo')
        if ordenar_por not in ['grupo', '-grupo', 'resultado', '-resultado']:
            ordenar_por = '-grupo'
            
        return qs.order_by(ordenar_por)

    def get_queryset(self):
        return self.model.objects.all()

    def apply_filters(self, qs):
        # Compatibilidad formato antiguo: {"estado": "PAGADO"}
        if not isinstance(self.filtros, dict) or 'conditions' not in self.filtros:
            for k, v in (self.filtros or {}).items():
                if k in self.filtros_permitidos:
                    qs = qs.filter(**{k: v})
            return qs

        # Formato complejo nuevo: {"logic": "and", "conditions": [...]}
        logic = self.filtros.get('logic', 'and').lower()
        conditions = self.filtros.get('conditions', [])
        
        if not conditions:
            return qs
            
        q_obj = Q()
        for cond in conditions:
            field = cond.get('field')
            operator = cond.get('operator', 'exact')
            value = cond.get('value')
            
            # Simple validation
            if field not in self.filtros_permitidos and not field.startswith('fecha_') and not field.startswith('categoria__') and not field.startswith('usuario__'):
                continue
                
            if operator == 'in' and isinstance(value, str):
                value = [v.strip() for v in value.split(',')]
            
            lookup = f"{field}__{operator}" if operator != 'exact' else field
            
            # Para fechas de creacion
            if field == 'fecha_creacion' and operator in ['gte', 'lte']:
                # ensure its treated well
                pass
                
            if logic == 'or':
                q_obj |= Q(**{lookup: value})
            else:
                q_obj &= Q(**{lookup: value})
                
        return qs.filter(q_obj)


@ReportRegistry.register_dinamico('pedidos', 'Pedidos y Ventas')
class PedidoReportBuilder(ModelReportBuilder):
    model = Pedido
    metricas = {
        'total': Sum(F('carrito__items__producto__precio') * F('carrito__items__cantidad'), output_field=DecimalField()),
        'conteo': Count('id', distinct=True)
    }
    agrupaciones = {
        'año': TruncYear('fecha_creacion'),
        'mes': TruncMonth('fecha_creacion'),
        'dia': TruncDay('fecha_creacion'),
        'estado': F('estado')
    }
    filtros_permitidos = ['estado', 'fecha_creacion', 'id']

    def get_queryset(self):
        qs = super().get_queryset()
        # Mantenemos comportamiento de filtrar cobradas si no se especifica estado en el modo viejo
        if not isinstance(self.filtros, dict) or 'conditions' not in self.filtros:
            if 'estado' not in self.filtros:
                return qs.filter(estado__in=ESTADOS_VENTA_COBRADA)
        return qs


@ReportRegistry.register_dinamico('productos', 'Inventario de Productos')
class ProductoReportBuilder(ModelReportBuilder):
    model = Producto
    metricas = {
        'stock': Sum('stock'),
        'conteo': Count('id', distinct=True)
    }
    agrupaciones = {
        'categoria': F('categoria__nombre'),
        'activo': F('activo')
    }
    filtros_permitidos = ['activo', 'categoria__nombre', 'stock', 'precio', 'nombre', 'id']


@ReportRegistry.register_dinamico('clientes', 'Clientes Registrados')
class ClienteReportBuilder(ModelReportBuilder):
    model = Cliente
    metricas = {
        'conteo': Count('id', distinct=True)
    }
    agrupaciones = {
        'año': TruncYear('fecha_registro'),
        'mes': TruncMonth('fecha_registro')
    }
    filtros_permitidos = ['fecha_registro', 'id', 'usuario__first_name']


@ReportRegistry.register_dinamico('facturas', 'Facturación y Pagos')
class FacturaReportBuilder(ModelReportBuilder):
    model = Factura
    metricas = {
        'total': Sum('monto_total'),
        'conteo': Count('nro', distinct=True)
    }
    agrupaciones = {
        'año': TruncYear('fecha'),
        'mes': TruncMonth('fecha'),
        'estado': F('estado')
    }
    filtros_permitidos = ['estado', 'fecha', 'monto_total', 'nro']

