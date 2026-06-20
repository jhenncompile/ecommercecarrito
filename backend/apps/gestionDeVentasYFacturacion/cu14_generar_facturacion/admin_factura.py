from django.contrib import admin
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.admin_base import TenantSafeAdmin
from .models.factura import Factura
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.models.tipo_pago import TipoPago
from .models.detalle_factura import DetalleFactura


class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura
    extra = 0
    readonly_fields = ('total',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'total')


@admin.register(Factura)
class FacturaAdmin(TenantSafeAdmin):
    list_display = ('nro', 'get_cliente_nombre', 'tipo_pago', 'monto_total', 'estado', 'fecha')
    list_filter = ('estado', 'fecha', 'tipo_pago')
    search_fields = ('nro', 'cliente__nombre', 'cliente__correo')
    readonly_fields = ('nro', 'fecha', 'hora', 'monto_total')
    inlines = [DetalleFacturaInline]
    
    fieldsets = (
        ('Documento', {
            'fields': ('nro', 'fecha', 'hora')
        }),
        ('InformaciÃ³n', {
            'fields': ('pedido', 'cliente', 'tipo_pago')
        }),
        ('Totales', {
            'fields': ('monto_total', 'moneda')
        }),
        ('Fiscal', {
            'fields': ('cuf', 'estado')
        }),
    )

    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre
    get_cliente_nombre.short_description = 'Cliente'


@admin.register(TipoPago)
class TipoPagoAdmin(TenantSafeAdmin):
    list_display = ('nombre', 'estado', 'descripcion')
    list_filter = ('estado',)
    search_fields = ('nombre',)
    
    fieldsets = (
        ('InformaciÃ³n', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
    )

