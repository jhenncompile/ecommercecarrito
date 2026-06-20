from apps.core.services import BaseService
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.factura import Factura, TipoPago
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.detalle_factura import DetalleFactura
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from django.db import connection
from apps.customers.clientes.models.cliente import Cliente
from django.db import transaction
from decimal import Decimal
import random
import string


class TipoPagoService(BaseService):
    """Servicio de Tipos de Pago."""
    
    def __init__(self):
        super().__init__(TipoPago)
    
    def obtener_activos(self):
        """Obtiene tipos de pago activos."""
        return TipoPago.objects.filter(estado='ACTIVO')


class FacturaService(BaseService):
    """Servicio de Facturas."""
    
    def __init__(self):
        super().__init__(Factura)
        self.tipo_pago_service = TipoPagoService()
    
    def generar_numero_factura(self):
        """Genera un número de factura único."""
        # Formato: FAC-YYYYMMDD-XXXXX
        from datetime import datetime
        fecha = datetime.now().strftime('%Y%m%d')
        aleatorio = ''.join(random.choices(string.digits, k=5))
        return f"FAC-{fecha}-{aleatorio}"
    
    @transaction.atomic
    def crear_factura_desde_pedido(self, pedido_id, tipo_pago_id=None):
        """
        Crea una factura a partir de un pedido.
        
        Incluye:
        - Número de factura único
        - Monto total del carrito
        - Detalles de cada item
        """
        pedido = Pedido.objects.get(id=pedido_id)
        
        # Validar que el pedido sea válido
        if not pedido.carrito or pedido.carrito.cantidad_items == 0:
            raise ValueError("El pedido no tiene items")
        
        # Obtener cliente del carrito
        cliente = pedido.carrito.cliente
        
        # Generar número de factura
        nro_factura = self.generar_numero_factura()
        
        # Calcular monto total
        monto_total = pedido.carrito.total_carrito
        
        # Obtener tipo de pago
        tipo_pago = None
        if tipo_pago_id:
            tipo_pago = TipoPago.objects.get(id=tipo_pago_id)
        
        # Crear factura
        factura = Factura.objects.create(
            nro=nro_factura,
            pedido=pedido,
            cliente=cliente,
            tipo_pago=tipo_pago,
            monto_total=monto_total,
            estado='VIGENTE'
        )
        
        # Crear detalles de factura (uno por cada item del carrito)
        for item in pedido.carrito.items.all():
            DetalleFactura.objects.create(
                factura=factura,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio,
                total=item.subtotal
            )
        
        return factura
    
    def anular_factura(self, factura_nro):
        """Anula una factura."""
        factura = self.obtener_por_numero(factura_nro)
        if factura.estado == 'ANULADA':
            raise ValueError("La factura ya está anulada")
        
        factura.estado = 'ANULADA'
        factura.save()
        return factura
    
    def obtener_por_numero(self, nro_factura):
        """Obtiene una factura por número."""
        try:
            return Factura.objects.get(nro=nro_factura)
        except Factura.DoesNotExist:
            raise ValueError(f"Factura {nro_factura} no encontrada")
    
    def obtener_por_cliente(self, cliente_id):
        """Obtiene todas las facturas de un cliente."""
        return Factura.objects.filter(cliente_id=cliente_id).order_by('-fecha')
    
    def obtener_por_estado(self, estado):
        """Obtiene facturas por estado."""
        return Factura.objects.filter(estado=estado).order_by('-fecha')
