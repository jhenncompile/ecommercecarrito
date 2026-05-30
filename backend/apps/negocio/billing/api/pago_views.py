import stripe
from django.db import connection
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django_tenants.utils import schema_context
import logging

from apps.negocio.ordenes.models.pedido import Pedido
from apps.negocio.ordenes.models.carrito import Carrito
from apps.negocio.ordenes.models.carrito_item import CarritoItem

logger = logging.getLogger(__name__)

class PagoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_stripe_key(self):
        key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        if not key:
            print("❌ ERROR: No se encontró STRIPE_SECRET_KEY en settings")
            return None
        stripe.api_key = key
        return key

    @action(detail=False, methods=['post'], url_path='create-payment-intent')
    def create_payment_intent(self, request):
        pedido_id = request.data.get('pedido_id')
        print(f"💳 Creando PaymentIntent para pedido: {pedido_id}")
        
        if not self._get_stripe_key():
            return Response({'error': 'Configuración de Stripe incompleta'}, status=500)

        try:
            pedido = Pedido.objects.get(id=pedido_id)
            if pedido.estado == 'PAGADO':
                return Response({'error': 'Este pedido ya ha sido pagado'}, status=400)

            # Calcular monto total
            monto_centavos = 0
            for item in pedido.carrito.items.all():
                if item.producto.precio:
                    monto_centavos += int(round(float(item.producto.precio) * 100 * item.cantidad))

            if monto_centavos == 0:
                return Response({'error': 'El monto del pedido es 0'}, status=400)

            # Crear el PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=monto_centavos,
                currency='bob',
                metadata={
                    'pedido_id': str(pedido.id),
                    'tenant': str(connection.schema_name)
                },
                automatic_payment_methods={
                    'enabled': True,
                },
            )

            return Response({
                'paymentIntent': intent.client_secret,
                'publishableKey': settings.STRIPE_PUBLISHABLE_KEY,
            })

        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado'}, status=404)
        except Exception as e:
            print(f"❌ Error creando PaymentIntent: {str(e)}")
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'], url_path='create-checkout-session')
    def create_checkout_session(self, request):
        pedido_id = request.data.get('pedido_id')
        print(f"📦 Procesando pago para pedido: {pedido_id}")
        
        if not self._get_stripe_key():
            return Response({'error': 'Configuración de Stripe incompleta'}, status=500)

        try:
            pedido = Pedido.objects.get(id=pedido_id)
            
            if pedido.estado == 'PAGADO':
                return Response({'error': 'Este pedido ya ha sido pagado'}, status=400)

            # Preparar items
            line_items = []
            if not hasattr(pedido, 'carrito') or not pedido.carrito:
                print("❌ ERROR: El pedido no tiene carrito")
                return Response({'error': 'El pedido no tiene un carrito asociado'}, status=400)

            for item in pedido.carrito.items.all():
                if not item.producto.precio:
                    print(f"⚠️ ADVERTENCIA: El producto {item.producto.nombre} no tiene precio.")
                    continue
                monto_centavos = int(round(float(item.producto.precio) * 100))
                line_items.append({
                    'price_data': {
                        'currency': 'bob',
                        'product_data': {
                            'name': item.producto.nombre,
                        },
                        'unit_amount': monto_centavos,
                    },
                    'quantity': item.cantidad,
                })

            if not line_items:
                return Response({'error': 'El carrito está vacío'}, status=400)

            # Crear sesión
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.data.get('success_url'),
                cancel_url=request.data.get('cancel_url'),
                metadata={
                    'pedido_id': str(pedido.id),
                    'tenant': str(connection.schema_name)
                }
            )
            
            pedido.stripe_session_id = checkout_session.id
            pedido.save()

            print(f"✅ Sesión de Stripe creada: {checkout_session.id}")
            return Response({'id': checkout_session.id, 'url': checkout_session.url})

        except Pedido.DoesNotExist:
            print(f"❌ ERROR: Pedido {pedido_id} no existe")
            return Response({'error': 'Pedido no encontrado'}, status=404)
        except stripe.error.StripeError as e:
            print(f"❌ STRIPE ERROR: {str(e)}")
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            import traceback
            print(f"❌ BACKEND CRITICAL ERROR creando sesión Stripe: {str(e)}")
            print(f"Datos recibidos: {request.data}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'], url_path='confirm-success', permission_classes=[IsAuthenticated])
    def confirm_success(self, request):
        pedido_id = request.data.get('pedido_id')
        tenant = request.data.get('tenant')
        
        if not pedido_id:
            return Response({'error': 'pedido_id es requerido'}, status=400)

        print(f"🔄 Confirmando éxito para pedido {pedido_id} en tenant {tenant or 'actual'}")
        
        try:
            if tenant:
                with schema_context(tenant):
                    self._marcar_pagado(pedido_id)
            else:
                self._marcar_pagado(pedido_id)
            return Response({'status': 'Pedido marcado como pagado'})
        except Exception as e:
            import traceback
            print(f"❌ Error confirmando éxito: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'], url_path='confirm-payment', permission_classes=[IsAuthenticated])
    def confirm_payment(self, request):
        """Alias para confirm-success utilizado por la app Flutter"""
        return self.confirm_success(request)

    @action(detail=False, methods=['post'], url_path='webhook', permission_classes=[AllowAny])
    def stripe_webhook(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

        try:
            if endpoint_secret and sig_header:
                event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            else:
                import json
                event = json.loads(payload)
        except Exception as e:
            print(f"❌ WEBHOOK ERROR: {str(e)}")
            return Response({'error': str(e)}, status=400)

        data_object = event.get('data', {}).get('object', {})
        if event.get('type') in ['checkout.session.completed', 'payment_intent.succeeded']:
            metadata = data_object.get('metadata', {})
            pedido_id = metadata.get('pedido_id')
            tenant = metadata.get('tenant')
            
            if pedido_id and tenant:
                with schema_context(tenant):
                    self._marcar_pagado(pedido_id)

        return Response(status=200)

    def _marcar_pagado(self, pedido_id):
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            if pedido.estado == 'PENDIENTE':
                pedido.estado = 'PAGADO'
                pedido.save()
                
                try:
                    from ..services.factura_service import FacturaService
                    from ..models.factura import TipoPago
                    tp = TipoPago.objects.filter(nombre__iexact='Stripe').first()
                    if not tp:
                        tp = TipoPago.objects.create(nombre='Stripe')
                    FacturaService().crear_factura_desde_pedido(pedido_id, tp.id)
                    print(f"📄 Factura generada para pedido {pedido_id}")
                    
                    # Enviar Notificación de Compra Exitosa al Cliente
                    try:
                        from apps.negocio.notificaciones.services.notification_service import send_notification
                        send_notification(
                            cliente=pedido.carrito.cliente,
                            titulo="Compra Exitosa",
                            mensaje=f"Tu pago por el pedido #{pedido.id} ha sido procesado exitosamente.",
                            tipo="PAGO"
                        )
                    except Exception as en:
                        print(f"⚠️ Error al enviar notificación de pago al cliente: {str(en)}")
                        
                    # Enviar Notificación de Nueva Venta al Vendedor
                    try:
                        from apps.customers.users.models.usuario import Usuario
                        from apps.negocio.notificaciones.services.notification_service import send_notification
                        
                        # Buscar los administradores/vendedores de este tenant
                        vendedores = Usuario.objects.filter(tenant__schema_name=connection.schema_name)
                        for vendedor in vendedores:
                            send_notification(
                                usuario=vendedor,
                                titulo="Nueva Venta 💰",
                                mensaje=f"{pedido.carrito.cliente.nombre} ha pagado el pedido #{pedido.id}.",
                                tipo="PEDIDO"
                            )
                    except Exception as env:
                        print(f"⚠️ Error al enviar notificación de pago al vendedor: {str(env)}")
                except Exception as ef:
                    print(f"⚠️ Error al generar factura: {str(ef)}")
        except Exception as e:
            print(f"❌ ERROR en _marcar_pagado: {str(e)}")
