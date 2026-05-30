import os
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from apps.negocio.notificaciones.models.notificacion import Notificacion
from apps.customers.users.models.device_token import DeviceToken

def _initialize_firebase():
    """
    Inicializa Firebase Admin SDK si aún no está inicializado.
    """
    if not firebase_admin._apps:
        # Intenta cargar credenciales de la variable de entorno o archivo
        cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', 'firebase-adminsdk.json')
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            print("⚠️ ADVERTENCIA: No se encontró firebase-adminsdk.json. Las notificaciones push no se enviarán.")

def send_notification(cliente=None, usuario=None, titulo="", mensaje="", tipo='SISTEMA'):
    """
    Guarda la notificación en base de datos local y envía push notification si tiene token.
    """
    if not cliente and not usuario:
        print("⚠️ No se puede enviar notificación sin cliente o usuario.")
        return None

    # 1. Guardar en base de datos (Notificación In-App)
    notif = Notificacion.objects.create(
        cliente=cliente,
        usuario=usuario,
        titulo=titulo,
        mensaje=mensaje,
        tipo=tipo
    )
    
    # 2. Enviar Push Notification (FCM)
    _initialize_firebase()
    if not firebase_admin._apps:
        return notif # No se configuró firebase
        
    if cliente:
        tokens = DeviceToken.objects.filter(cliente=cliente).values_list('token', flat=True)
    elif usuario:
        tokens = DeviceToken.objects.filter(usuario=usuario).values_list('token', flat=True)
    else:
        tokens = []

    if not tokens:
        return notif

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=titulo,
            body=mensaje,
        ),
        data={
            'type': tipo,
            'notificacion_id': str(notif.id)
        },
        tokens=list(tokens),
    )

    try:
        response = messaging.send_each_for_multicast(message)
        print(f"✅ Notificación enviada a {response.success_count} dispositivos")
    except Exception as e:
        print(f"❌ Error al enviar notificación FCM: {e}")

    return notif
