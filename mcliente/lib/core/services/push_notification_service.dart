import 'dart:developer';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../../main.dart';
import '../network/api_client.dart';
import '../constants/api_constants.dart';

/// Define un background handler de forma top-level como lo requiere Firebase
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  // Asegúrate de que Firebase esté inicializado antes de usar otros servicios de Firebase en background.
  log("Manejando un mensaje en segundo plano: ${message.messageId}");
  // Aquí podemos añadir lógica si queremos guardar en base de datos local o procesar algo
}

class PushNotificationService {
  static final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();

  static Future<void> initializeApp() async {
    // 1. Solicitar permisos (Principalmente para iOS y Android 13+)
    await _requestPermission();

    // 2. Configurar notificaciones locales (heads-up para Android en primer plano)
    await _initializeLocalNotifications();

    // 3. Manejar mensaje en segundo plano o cuando la app está terminada
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // 4. Manejar mensajes cuando la app está en primer plano
    FirebaseMessaging.onMessage.listen(_onMessageHandler);

    // 5. Manejar cuando el usuario toca una notificación en segundo plano y la app se abre
    FirebaseMessaging.onMessageOpenedApp.listen(_onMessageOpenApp);

    // 6. Manejar si la app fue abierta desde una notificación cuando estaba terminada
    final RemoteMessage? initialMessage = await _firebaseMessaging.getInitialMessage();
    if (initialMessage != null) {
      _onMessageOpenApp(initialMessage);
    }

    // Opcional: Obtener el token de FCM e imprimirlo
    final token = await getToken();
    log("FCM Token (MCliente): $token");
    if (token != null) {
      await registerTokenWithBackend(token);
    }
  }

  static Future<void> registerTokenWithBackend(String token) async {
    try {
      final apiClient = ApiClient();
      await apiClient.post('${ApiConstants.mainBaseUrl}/device-token/', {'token': token});
      log("Token registrado en el backend exitosamente.");
    } catch (e) {
      log("Error al registrar token en el backend: $e");
    }
  }

  static Future<void> _requestPermission() async {
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );
    log('Estado del permiso de notificaciones: ${settings.authorizationStatus}');
  }

  static Future<void> _initializeLocalNotifications() async {
    // Usa el ícono por defecto de lanzamiento de la app (se debe asegurar que exista en mipmap)
    const AndroidInitializationSettings androidInitSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    
    // Para iOS (si fuera aplicable en el futuro)
    const DarwinInitializationSettings iosInitSettings = DarwinInitializationSettings();

    const InitializationSettings initSettings = InitializationSettings(
      android: androidInitSettings,
      iOS: iosInitSettings,
    );

    await _localNotifications.initialize(
      settings: initSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) {
        // Manejar toque en la notificación generada localmente (app en primer plano)
        if (response.payload != null) {
          log("Notificación local tocada con payload: ${response.payload}");
          // _handleNotificationTypeData(response.payload);
        }
      },
    );
  }

  static void _onMessageHandler(RemoteMessage message) {
    log("Mensaje recibido en primer plano: ${message.notification?.title}");
    
    if (message.notification != null) {
      _showLocalNotification(message);
    }
    
    _handleNotificationType(message.data);
  }

  static void _onMessageOpenApp(RemoteMessage message) {
    log("Notificación tocada y app abierta (desde segundo plano)");
    _handleNotificationType(message.data);
  }

  /// Procesa los datos extra (payload) recibidos
  static void _handleNotificationType(Map<String, dynamic> data) {
    if (data.isEmpty) return;

    final String? type = data['type'];
    log("Procesando tipo de notificación en MCliente: $type");
    
    // Navegar usando navigatorKey
    if (navigatorKey.currentState != null) {
      if (type == 'PAGO' || type == 'PEDIDO') {
        navigatorKey.currentState!.pushNamed('/pedidos');
      } else {
        navigatorKey.currentState!.pushNamed('/notificaciones');
      }
    }
  }

  static Future<void> _showLocalNotification(RemoteMessage message) async {
    final AndroidNotificationDetails androidPlatformChannelSpecifics = AndroidNotificationDetails(
      'high_importance_channel', // id
      'High Importance Notifications', // nombre
      channelDescription: 'Este canal se usa para notificaciones importantes.',
      importance: Importance.max,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher', // IMPORTANTE: debe coincidir
    );

    final NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
      iOS: const DarwinNotificationDetails(),
    );

    await _localNotifications.show(
      id: message.hashCode,
      title: message.notification?.title,
      body: message.notification?.body,
      notificationDetails: platformChannelSpecifics,
      payload: message.data.toString(),
    );
  }

  static Future<String?> getToken() async {
    return await _firebaseMessaging.getToken();
  }
}
