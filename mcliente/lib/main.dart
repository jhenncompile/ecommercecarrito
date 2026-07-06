import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'core/services/push_notification_service.dart';

import 'gestion_usuario/screens/login_screen.dart';
import 'gestion_usuario/screens/registration_screen.dart';
import 'gestion_usuario/screens/profile_screen.dart';
import 'gestion_producto/screens/storefront_screen.dart';
import 'gestion_producto/screens/cart_screen.dart';
import 'gestion_producto/screens/orders_screen.dart';
import 'gestion_producto/screens/shop_list_screen.dart';
import 'gestion_usuario/screens/notifications_screen.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  await dotenv.load(fileName: "assets/.env");
  
  Stripe.publishableKey = dotenv.env['STRIPE_PUBLISHABLE_KEY'] ?? "";
  await Stripe.instance.applySettings();

  // Iniciar la app primero para evitar la pantalla negra
  runApp(const MyApp());
  
  // Solicitar permisos y configurar notificaciones DESPUÉS de que la UI ya se esté renderizando
  PushNotificationService.initializeApp();
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MiQhatu Cliente',
      theme: AppTheme.themeData,
      debugShowCheckedModeBanner: false,
      navigatorKey: navigatorKey,
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/registro': (context) => const RegistrationScreen(),
        '/tiendas': (context) => const ShopListScreen(),
        '/tienda': (context) => const StorefrontScreen(),
        '/carrito': (context) => const CartScreen(),
        '/pedidos': (context) => const OrdersScreen(),
        '/perfil': (context) => const ProfileScreen(),
        '/notificaciones': (context) => const NotificationsScreen(),
      },
    );
  }
}
