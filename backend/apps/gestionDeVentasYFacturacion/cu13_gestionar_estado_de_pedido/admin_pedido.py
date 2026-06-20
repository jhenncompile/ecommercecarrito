from django.contrib import admin
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.admin_base import TenantSafeAdmin
from .models.pedido import Pedido


@admin.register(Pedido)
class PedidoAdmin(TenantSafeAdmin):
    list_display = ('id', 'cliente_nombre', 'estado', 'total_pedido', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('carrito__cliente__nombre', 'carrito__cliente__correo')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'cliente_nombre', 'total_pedido', 'cantidad_items')
    
    fieldsets = (
        ('Orden', {
            'fields': ('carrito', 'cliente_nombre')
        }),
        ('Estado', {
            'fields': ('estado', 'observaciones')
        }),
        ('Resumen', {
            'fields': ('cantidad_items', 'total_pedido')
        }),
        ('AuditorÃ­a', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def cliente_nombre(self, obj):
        return obj.carrito.cliente.nombre if obj.carrito else 'N/A'
    cliente_nombre.short_description = 'Cliente'

    def total_pedido(self, obj):
        return f"${obj.carrito.total_carrito:.2f}" if obj.carrito else 'N/A'
    total_pedido.short_description = 'Total'

    def cantidad_items(self, obj):
        return obj.carrito.cantidad_items if obj.carrito else 'N/A'
    cantidad_items.short_description = 'Items'

