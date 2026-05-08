import stripe
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models.pedido import Pedido
from ..models.factura import Factura
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

class PagoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='create-checkout-session')
    def create_checkout_session(self, request):
        """
        Crea una sesión de pago en Stripe para un pedido específico.
        """
        pedido_id = request.data.get('pedido_id')
        if not pedido_id:
            return Response({'error': 'pedido_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pedido = Pedido.objects.get(id=pedido_id)
            # Validar que el pedido pertenezca al usuario (opcional, dependiendo de la lógica)
            
            # Construir ítems para Stripe
            line_items = []
            for item in pedido.items.all():
                line_items.append({
                    'price_data': {
                        'currency': 'bob', # O la moneda configurada
                        'product_data': {
                            'name': item.producto.nombre,
                            'description': item.producto.descripcion[:100] if item.producto.descripcion else '',
                        },
                        'unit_amount': int(item.precio_unitario * 100), # Stripe usa centavos
                    },
                    'quantity': item.cantidad,
                })

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.data.get('success_url', 'http://localhost:3000/success'),
                cancel_url=request.data.get('cancel_url', 'http://localhost:3000/cancel'),
                metadata={
                    'pedido_id': pedido.id,
                    'tenant': getattr(settings, 'TENANT_NAME', 'unknown')
                }
            )

            return Response({'id': checkout_session.id, 'url': checkout_session.url})
        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Stripe Session Error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='webhook', permission_classes=[AllowAny])
    def stripe_webhook(self, request):
        """
        Recibe notificaciones de Stripe. Si no hay WEBHOOK_SECRET, 
        se procesa sin verificar firma (útil para pruebas locales sin CLI de Stripe).
        """
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        if endpoint_secret:
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
            try:
                event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Si no hay secreto, confiamos en el payload (SOLO PARA DESARROLLO/SANDBOX)
            import json
            try:
                event = json.loads(payload)
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        # Manejar el evento
        event_type = event.get('type') if not endpoint_secret else event['type']
        data_object = event.get('data', {}).get('object', {}) if not endpoint_secret else event['data']['object']

        if event_type == 'checkout.session.completed':
            pedido_id = data_object.get('metadata', {}).get('pedido_id')
            if pedido_id:
                self._marcar_pagado(pedido_id)

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='confirm-success')
    def confirm_success(self, request):
        """
        Endpoint de respaldo para confirmar pago cuando el cliente regresa a la app.
        """
        pedido_id = request.data.get('pedido_id')
        if pedido_id:
            self._marcar_pagado(pedido_id)
            return Response({'status': 'ok'})
        return Response({'error': 'no id'}, status=400)

    def _marcar_pagado(self, pedido_id):
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.estado = 'pagado'
            pedido.save()
            logger.info(f"Pedido {pedido_id} marcado como PAGADO")
        except Pedido.DoesNotExist:
            pass
