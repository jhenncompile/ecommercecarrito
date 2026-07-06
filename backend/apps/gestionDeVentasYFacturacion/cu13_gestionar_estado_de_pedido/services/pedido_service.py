from apps.core.services import BaseService
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido, Carrito
from django.db import transaction


class PedidoService(BaseService):
    """Servicio de Pedidos."""
    
    def __init__(self):
        super().__init__(Pedido)
    
    def crear_pedido_desde_carrito(self, carrito_id):
        """Crea un pedido a partir de un carrito abierto."""
        carrito = Carrito.objects.get(id=carrito_id)
        
        if carrito.estado != 'ABIERTO':
            raise ValueError(f"El carrito debe estar ABIERTO. Estado actual: {carrito.estado}")
        
        if carrito.cantidad_items == 0:
            raise ValueError("No se puede crear un pedido de un carrito vacío")
            
        self._verificar_limite_facturacion(carrito.total_carrito)
        
        # Descontar stock de los items y notificar stock bajo si aplica
        for item in carrito.items.all():
            producto = item.producto
            if producto.stock >= item.cantidad:
                producto.stock -= item.cantidad
                producto.save()
                if producto.stock <= 6:
                    self._notificar_stock_bajo(producto)
            else:
                raise ValueError(f"Stock insuficiente para {producto.nombre}.")

        # Crear pedido
        pedido = Pedido.objects.create(
            carrito=carrito,
            estado='PENDIENTE'
        )
        
        # Cerrar carrito
        carrito.estado = 'CERRADO'
        carrito.save()
        
        # Notificar nueva venta
        self._notificar_nueva_venta(pedido)
        
        return pedido

    def crear_pedido_directo(self, cliente_id, items, envio=None):
        """Crea un carrito y un pedido en un solo paso.

        `envio` (opcional) es un dict con la logística del checkout:
        {tipo_envio, costo_envio, ciudad_envio, zona_envio}
        """
        from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito_item import CarritoItem
        from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
        from apps.customers.clientes.models.cliente import Cliente

        with transaction.atomic():
            cliente = Cliente.objects.get(id=cliente_id)
            carrito = Carrito.objects.create(cliente=cliente, estado='CERRADO')
            
            for item in items:
                prod_id = item.get('producto_id') or item.get('producto')
                if not prod_id:
                    raise ValueError("El item no contiene 'producto_id'")
                producto = Producto.objects.select_for_update().get(id=prod_id)
                cantidad_solicitada = int(item['cantidad'])
                
                if producto.stock < cantidad_solicitada:
                    raise ValueError(f"Stock insuficiente para {producto.nombre}. Solicitado: {cantidad_solicitada}, Disponible: {producto.stock}")
                    
                # Descontar el stock
                producto.stock -= cantidad_solicitada
                producto.save()
                
                # Low Stock Notification
                if producto.stock <= 6:
                    self._notificar_stock_bajo(producto)
                
                CarritoItem.objects.create(
                    carrito=carrito,
                    producto=producto,
                    cantidad=cantidad_solicitada
                )
                
            self._verificar_limite_facturacion(carrito.total_carrito)

            envio = envio or {}
            pedido = Pedido.objects.create(
                carrito=carrito,
                estado='PENDIENTE',
                tipo_envio=envio.get('tipo_envio') or None,
                costo_envio=envio.get('costo_envio') or 0,
                ciudad_envio=envio.get('ciudad_envio') or None,
                zona_envio=envio.get('zona_envio') or None,
            )

            # Notificar nueva venta al vendedor
            self._notificar_nueva_venta(pedido)

            return pedido

    def _notificar_stock_bajo(self, producto):
        from apps.gestionDeReportes.cu18_gestionar_notificaciones.services.notification_service import send_notification
        from django.db import connection
        from apps.customers.models import Client
        from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.models.usuario import Usuario
        
        schema = connection.schema_name
        if schema == 'public': return
        
        try:
            tenant = Client.objects.get(schema_name=schema)
            vendedores = Usuario.objects.filter(tenant=tenant, is_active=True)
            for vendedor in vendedores:
                send_notification(
                    usuario=vendedor,
                    titulo="⚠️ Alerta de Stock Bajo",
                    mensaje=f"El producto '{producto.nombre}' tiene solo {producto.stock} unidades disponibles.",
                    tipo="STOCK_BAJO"
                )
        except Exception as e:
            print(f"Error al enviar notificacion de stock bajo: {str(e)}")

    def _notificar_nueva_venta(self, pedido):
        from apps.gestionDeReportes.cu18_gestionar_notificaciones.services.notification_service import send_notification
        from django.db import connection
        from apps.customers.models import Client
        from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.models.usuario import Usuario
        
        schema = connection.schema_name
        if schema == 'public': return
        
        try:
            tenant = Client.objects.get(schema_name=schema)
            vendedores = Usuario.objects.filter(tenant=tenant, is_active=True)
            for vendedor in vendedores:
                send_notification(
                    usuario=vendedor,
                    titulo="💰 ¡Nueva Venta Registrada!",
                    mensaje=f"Se ha registrado un nuevo pedido (#{pedido.id}) por un total de Bs. {pedido.carrito.total_carrito}.",
                    tipo="NUEVA_VENTA"
                )
        except Exception as e:
            print(f"Error al enviar notificacion de nueva venta: {str(e)}")

    def cambiar_estado(self, pedido_id, nuevo_estado):
        """Cambia el estado de un pedido."""
        estados_validos = ['PENDIENTE', 'PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO', 'CANCELADO']
        
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado inválido. Válidos: {estados_validos}")
        
        pedido = self.obtener(pedido_id)
        estado_anterior = pedido.estado
        pedido.estado = nuevo_estado
        pedido.save()
        
        # Notificar al cliente si el estado cambia a algo relevante (PROCESADO, ENVIADO, ENTREGADO, CANCELADO)
        if estado_anterior != nuevo_estado and nuevo_estado in ['PROCESADO', 'ENVIADO', 'ENTREGADO', 'CANCELADO']:
            try:
                from apps.gestionDeReportes.cu18_gestionar_notificaciones.services.notification_service import send_notification
                mensajes = {
                    'PROCESADO': 'ha sido procesado y está siendo preparado.',
                    'ENVIADO': 'ha sido enviado y está en camino hacia tu dirección.',
                    'ENTREGADO': 'ha sido entregado con éxito. ¡Gracias por tu compra!',
                    'CANCELADO': 'ha sido cancelado.'
                }
                
                send_notification(
                    cliente=pedido.carrito.cliente,
                    titulo=f"Actualización de Pedido #{pedido.id}",
                    mensaje=f"Tu pedido {mensajes.get(nuevo_estado, 'ha cambiado de estado.')}",
                    tipo="PEDIDO"
                )
            except Exception as e:
                print(f" Error al notificar cambio de estado: {str(e)}")
                
        return pedido
    
    def obtener_por_cliente(self, cliente_id):
        """Obtiene todos los pedidos de un cliente."""
        return Pedido.objects.filter(carrito__cliente_id=cliente_id).order_by('-fecha_creacion')
    
    def obtener_por_estado(self, estado):
        """Obtiene pedidos por estado."""
        return Pedido.objects.filter(estado=estado).order_by('-fecha_creacion')

    def _verificar_limite_facturacion(self, total_nuevo_pedido):
        from django.db import connection
        from apps.customers.models import Client
        from django.utils.timezone import now
        from rest_framework.exceptions import ValidationError

        schema = connection.schema_name
        if schema == 'public':
            return
            
        try:
            tenant = Client.objects.get(schema_name=schema)
        except Client.DoesNotExist:
            return
            
        if not tenant.plan:
            return

        current_day = now().date()
        
        pedidos_dia = Pedido.objects.filter(
            fecha_creacion__date=current_day,
            estado__in=['PENDIENTE', 'PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO']
        )
        
        total_facturado = sum(p.carrito.total_carrito for p in pedidos_dia)
        cantidad_ventas = pedidos_dia.count()
        
        # Verificar límite de facturación (si aplica)
        if tenant.plan.facturacion_max is not None:
            if (float(total_facturado) + float(total_nuevo_pedido)) > float(tenant.plan.facturacion_max):
                tenant.limite_alcanzado_fecha = current_day
                tenant.save()
                raise ValidationError({"limite_alcanzado": f"Has superado el límite de facturación diaria de tu plan ({tenant.plan.nombre}): ${tenant.plan.facturacion_max}. Has facturado ${total_facturado} hoy. Este pedido es de ${total_nuevo_pedido}. Por favor mejora tu suscripción."})

        # Verificar límite de ventas diarias (si aplica)
        if tenant.plan.ventas_max is not None:
            if (cantidad_ventas + 1) > tenant.plan.ventas_max:
                tenant.limite_alcanzado_fecha = current_day
                tenant.save()
                raise ValidationError({"limite_alcanzado": f"Has superado el límite de ventas diarias de tu plan ({tenant.plan.nombre}): {tenant.plan.ventas_max} ventas/día. Llevas {cantidad_ventas} hoy. Por favor mejora tu suscripción."})
