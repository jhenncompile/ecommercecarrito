import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'gestion_usuario/screens/login_screen.dart';
import 'gestion_usuario/screens/registration_screen.dart';
import 'gestion_usuario/screens/profile_screen.dart';
import 'gestion_producto/screens/storefront_screen.dart';
import 'gestion_producto/screens/cart_screen.dart';
import 'gestion_producto/screens/orders_screen.dart';
import 'gestion_producto/screens/shop_list_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await dotenv.load(fileName: "assets/.env");
  
  Stripe.publishableKey = dotenv.env['STRIPE_PUBLISHABLE_KEY'] ?? "";
  await Stripe.instance.applySettings();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MiQhatu Cliente',
      theme: AppTheme.themeData,
      debugShowCheckedModeBanner: false,
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/registro': (context) => const RegistrationScreen(),
        '/tiendas': (context) => const ShopListScreen(),
        '/tienda': (context) => const StorefrontScreen(),
        '/carrito': (context) => const CartScreen(),
        '/pedidos': (context) => const OrdersScreen(),
        '/perfil': (context) => const ProfileScreen(),
      },
    );
  }
}
