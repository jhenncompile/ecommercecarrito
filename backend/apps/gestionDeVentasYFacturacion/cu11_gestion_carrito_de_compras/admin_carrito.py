from django.contrib import admin
from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.admin_base import TenantSafeAdmin
from .models.carrito import Carrito
from .models.carrito_item import CarritoItem


class CarritoItemInline(admin.TabularInline):
    model = CarritoItem
    extra = 0
    readonly_fields = ('fecha_agregado', 'subtotal')
    fields = ('producto', 'cantidad', 'subtotal', 'fecha_agregado')


@admin.register(Carrito)
class CarritoAdmin(TenantSafeAdmin):
    list_display = ('id', 'cliente', 'estado', 'cantidad_items', 'total_carrito', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('cliente__nombre', 'cliente__correo')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'cantidad_items', 'total_carrito')
    inlines = [CarritoItemInline]
    
    fieldsets = (
        ('InformaciÃ³n', {
            'fields': ('cliente', 'estado')
        }),
        ('CÃ¡lculos', {
            'fields': ('cantidad_items', 'total_carrito')
        }),
        ('Fecha', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

