import 'dart:developer';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../../main.dart';
import '../network/api_client.dart';
import '../constants/api_constants.dart';

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  log("Manejando un mensaje en segundo plano (Vendedor): ${message.messageId}");
}

class PushNotificationService {
  static final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();

  static Future<void> initializeApp() async {
    await _requestPermission();
    await _initializeLocalNotifications();

    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
    FirebaseMessaging.onMessage.listen(_onMessageHandler);
    FirebaseMessaging.onMessageOpenedApp.listen(_onMessageOpenApp);

    final RemoteMessage? initialMessage = await _firebaseMessaging.getInitialMessage();
    if (initialMessage != null) {
      _onMessageOpenApp(initialMessage);
    }

    final token = await getToken();
    log("FCM Token (Movil Vendedor): $token");
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
    );
    log('Estado del permiso de notificaciones (Vendedor): ${settings.authorizationStatus}');
  }

  static Future<void> _initializeLocalNotifications() async {
    const AndroidInitializationSettings androidInitSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const DarwinInitializationSettings iosInitSettings = DarwinInitializationSettings();
    const InitializationSettings initSettings = InitializationSettings(android: androidInitSettings, iOS: iosInitSettings);

    await _localNotifications.initialize(
      settings: initSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) {
        if (response.payload != null) {
          log("Notificación local tocada (Vendedor) con payload: ${response.payload}");
        }
      },
    );
  }

  static void _onMessageHandler(RemoteMessage message) {
    log("Mensaje recibido en primer plano (Vendedor): ${message.notification?.title}");
    if (message.notification != null) {
      _showLocalNotification(message);
    }
    _handleNotificationType(message.data);
  }

  static void _onMessageOpenApp(RemoteMessage message) {
    log("Notificación tocada y app abierta (Vendedor)");
    _handleNotificationType(message.data);
  }

  static void _handleNotificationType(Map<String, dynamic> data) {
    if (data.isEmpty) return;

    final String? type = data['type'];
    log("Procesando tipo de notificación en Vendedor: $type");
    
    // Lógica de ruteo para el vendedor
    if (navigatorKey.currentState != null) {
      if (type == 'NUEVA_VENTA') {
        // navigatorKey.currentState!.pushNamed('/ventas');
      } else {
        navigatorKey.currentState!.pushNamed('/notificaciones');
      }
    }
  }

  static Future<void> _showLocalNotification(RemoteMessage message) async {
    final AndroidNotificationDetails androidPlatformChannelSpecifics = AndroidNotificationDetails(
      'seller_high_importance_channel',
      'Alertas de Vendedor',
      channelDescription: 'Alertas importantes para la tienda y ventas.',
      importance: Importance.max,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
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
