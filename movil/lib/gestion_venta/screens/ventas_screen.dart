import 'package:flutter/material.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/widgets/display/app_coming_soon.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';
import 'dart:convert';

class VentasScreen extends StatefulWidget {
  const VentasScreen({super.key});

  @override
  State<VentasScreen> createState() => _VentasScreenState();
}

class _VentasScreenState extends State<VentasScreen> {
  String _storeName = 'Cargando...';
  String _userName = 'Admin';
  final AuthRepository _authRepository = AuthRepository();

  @override
  void initState() {
    super.initState();
    _inicializar();
  }

  Future<void> _inicializar() async {
    final schemaName = await _authRepository.getSchemaName();
    String decodedUser = 'Admin';
    final token = await _authRepository.getAccessToken();
    if (token != null) {
      final payload = _decodeJwt(token);
      if (payload != null) {
        decodedUser = payload['full_name'] ?? payload['username'] ?? 'Admin';
      }
    }
    setState(() {
      _storeName = _formatStoreName(schemaName ?? '');
      _userName = decodedUser;
    });
  }

  String _formatStoreName(String schema) {
    if (schema.isEmpty) return 'Mi Tienda';
    return schema.split(RegExp(r'[x_]+')).map((word) {
      if (word.isEmpty) return '';
      return word[0].toUpperCase() + word.substring(1).toLowerCase();
    }).join(' ');
  }

  Map<String, dynamic>? _decodeJwt(String token) {
    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;
      var payload = parts[1];
      while (payload.length % 4 != 0) {
        payload += '=';
      }
      return jsonDecode(utf8.decode(base64Url.decode(payload)));
    } catch (_) {
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppDashboardLayout(
      brandName: 'MiQhatu',
      tenantValue: _storeName,
      userName: _userName,
      sidebarItems: [
        AppSidebarItem(
          icon: Icons.dashboard,
          label: 'Panel',
          onTap: () => Navigator.pushReplacementNamed(context, '/dashboard'),
        ),
        AppSidebarItem(
          icon: Icons.inventory_2,
          label: 'Productos',
          onTap: () => Navigator.pushReplacementNamed(context, '/productos'),
        ),
        AppSidebarItem(
          icon: Icons.category,
          label: 'Categorías',
          onTap: () => Navigator.pushReplacementNamed(context, '/categorias'),
        ),
        AppSidebarItem(
          icon: Icons.list_alt,
          label: 'Inventario',
          onTap: () => Navigator.pushReplacementNamed(context, '/inventario'),
        ),
        AppSidebarItem(
          icon: Icons.shopping_cart,
          label: 'Ventas',
          isActive: true,
          onTap: () => Navigator.pushReplacementNamed(context, '/ventas'),
        ),
        AppSidebarItem(
          icon: Icons.people,
          label: 'Clientes',
          onTap: () => Navigator.pushReplacementNamed(context, '/clientes'),
        ),
        AppSidebarItem(
          icon: Icons.bar_chart,
          label: 'Reportes',
          onTap: () => Navigator.pushReplacementNamed(context, '/reportes'),
        ),
        AppSidebarItem(
          icon: Icons.trending_up,
          label: 'Predicciones',
          onTap: () => Navigator.pushReplacementNamed(context, '/predicciones'),
        ),
        AppSidebarItem(
          icon: Icons.settings,
          label: 'Configuración',
          onTap: () => Navigator.pushReplacementNamed(context, '/configuracion'),
        ),
        AppSidebarItem(
          icon: Icons.logout,
          label: 'Salir',
          isLogout: true,
          onTap: () async {
            await _authRepository.logout();
            if (!context.mounted) return;
            Navigator.pushReplacementNamed(context, '/login');
          },
        ),
      ],
      body: const AppComingSoon(
        icon: Icons.shopping_cart,
        title: 'Ventas y Facturación',
        description: 'Registro completo de ventas, emisión de facturas SIN/QR, seguimiento de pedidos y gestión de devoluciones.',
        accentColor: Colors.green,
        features: [
          'Registro de ventas',
          'Facturación electrónica SIN',
          'Pagos con QR',
          'Gestión de pedidos',
          'Historial de transacciones',
          'Devoluciones y créditos',
        ],
      ),
    );
  }
}
