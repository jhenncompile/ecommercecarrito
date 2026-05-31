import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'core/services/push_notification_service.dart';

// 1. Importamos tu tema global
import 'core/theme/app_theme.dart';

// 2. Importamos tus pantallas
import 'gestion_usuario/screens/login_screen.dart';
import 'gestion_usuario/screens/recuperar_password_screen.dart';
import 'gestion_usuario/screens/crear_tienda_screen.dart';
import 'dashboard/screens/dashboard_screen.dart';

import 'gestion_usuario/screens/configuracion_screen.dart';
import 'gestion_producto/screens/productos_screen.dart';
import 'gestion_venta/screens/ventas_screen.dart';
import 'gestion_cliente/screens/clientes_screen.dart';
import 'gestion_reporte/screens/reportes_screen.dart';
import 'gestion_producto/screens/inventario_screen.dart';
import 'gestion_producto/screens/categorias_screen.dart';
import 'gestion_usuario/screens/notifications_screen.dart';
import 'gestion_reporte/screens/predicciones_screen.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  await PushNotificationService.initializeApp();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MiQhatu App',
      // ¡Aquí inyectamos todo el UI Kit que creaste!
      theme: AppTheme.themeData, 
      
      // Quitamos la etiqueta molesta de "DEBUG" arriba a la derecha
      debugShowCheckedModeBanner: false,
      navigatorKey: navigatorKey,
      
      // ── LA LÓGICA DE RUTAS ──
      
      // 1. Definimos con qué pantalla arranca la app
      initialRoute: '/login', 
      
      // 2. El "Mapa" de rutas. Asigna un string a cada pantalla
      routes: {
        '/login': (context) => const LoginScreen(),
        '/recuperar-password': (context) => const RecuperarPasswordScreen(),
        '/crear-tienda': (context) => const CrearTiendaScreen(),
        '/dashboard': (context) => const DashboardScreen(),
        '/productos': (context) => const ProductosScreen(),
        '/categorias': (context) => const CategoriasScreen(),
        '/ventas': (context) => const VentasScreen(),
        '/clientes': (context) => const ClientesScreen(),
        '/reportes': (context) => const ReportesScreen(),
        '/predicciones': (context) => const PrediccionesScreen(),
        '/inventario': (context) => const InventarioScreen(),
        '/configuracion': (context) => const ConfiguracionScreen(),
        '/notificaciones': (context) => const NotificationsScreen(),
      },
    );
  }
}