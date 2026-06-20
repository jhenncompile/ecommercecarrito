from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.gestionDeReportes.cu18_gestionar_notificaciones.services.notification_service import send_notification

@receiver(pre_save, sender=Pedido)
def capture_previous_estado(sender, instance, **kwargs):
    if instance.id:
        try:
            old_instance = Pedido.objects.get(id=instance.id)
            instance._old_estado = old_instance.estado
        except Pedido.DoesNotExist:
            instance._old_estado = None
    else:
        instance._old_estado = None

@receiver(post_save, sender=Pedido)
def notify_on_estado_change(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_old_estado'):
        old_estado = instance._old_estado
        new_estado = instance.estado
        
        # Avisar sobre cambios a cualquier estado importante
        estados_importantes = ['PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO', 'CANCELADO']
        if old_estado != new_estado and new_estado in estados_importantes:
            cliente = instance.carrito.cliente
            mensaje = f"Tu pedido #{instance.id} ahora está: {new_estado}."
            
            titulo = "Actualización de tu pedido"
            if new_estado == 'ENVIADO':
                titulo = "Pedido en camino 🚚"
            elif new_estado == 'ENTREGADO':
                titulo = "Pedido entregado ✅"
            elif new_estado == 'PAGADO':
                titulo = "Pago confirmado 💳"
            elif new_estado == 'PROCESADO':
                titulo = "Pedido en preparación 📦"
            elif new_estado == 'CANCELADO':
                titulo = "Pedido cancelado ❌"
                
            try:
                send_notification(
                    cliente=cliente,
                    titulo=titulo,
                    mensaje=mensaje,
                    tipo='PEDIDO'
                )
            except Exception as e:
                print(f"Error al enviar notificación de cambio de estado: {e}")
