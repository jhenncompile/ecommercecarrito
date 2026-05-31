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
        cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
        
        posibles_rutas = [
            cred_path,
            os.path.join(settings.BASE_DIR, "credenciales", "si2parcial-9e9e9-firebase-adminsdk-fbsvc-c5fcfdacf9.json"),
            os.path.join(settings.BASE_DIR, "firebase-adminsdk.json"),
            os.path.join(settings.BASE_DIR, "credenciales", "firebase-adminsdk.json")
        ]
        
        found_path = None
        for p in posibles_rutas:
            if p and os.path.exists(p):
                found_path = p
                break

        if found_path:
            cred = credentials.Certificate(found_path)
            firebase_admin.initialize_app(cred)
            print(f"✅ Firebase inicializado correctamente desde: {found_path}")
        else:
            print(f"⚠️ ADVERTENCIA: No se encontró el archivo de Firebase. Rutas buscadas: {[p for p in posibles_rutas if p]}")

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
        
    # DeviceToken vive en SHARED_APPS (esquema public), hay que buscarlo allí.
    # Usamos IDs para evitar problemas de FK entre schemas.
    from django_tenants.utils import schema_context
    cliente_id = cliente.id if cliente else None
    usuario_id = usuario.id if usuario else None

    with schema_context('public'):
        if cliente_id:
            tokens = list(DeviceToken.objects.filter(cliente_id=cliente_id).values_list('token', flat=True))
        elif usuario_id:
            tokens = list(DeviceToken.objects.filter(usuario_id=usuario_id).values_list('token', flat=True))
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
