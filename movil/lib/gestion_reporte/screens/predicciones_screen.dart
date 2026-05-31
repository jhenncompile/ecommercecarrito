import 'dart:convert';
import 'package:flutter/material.dart';

// UI Kit
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';

// Business Logic
import '../../gestion_usuario/repositories/auth_repository.dart';

// Widgets
import '../widgets/prediccion_tab.dart';

class PrediccionesScreen extends StatefulWidget {
  const PrediccionesScreen({super.key});

  @override
  State<PrediccionesScreen> createState() => _PrediccionesScreenState();
}

class _PrediccionesScreenState extends State<PrediccionesScreen> with SingleTickerProviderStateMixin {
  String _storeName = 'Cargando...';
  String _userName = 'Admin';
  final AuthRepository _authRepository = AuthRepository();
  
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        setState(() {}); // Re-render to show correct tab
      }
    });
    _inicializar();
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
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

    if (mounted) {
      setState(() {
        _storeName = _formatStoreName(schemaName ?? '');
        _userName = decodedUser;
      });
    }
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
          isActive: true,
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
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── HEADER ──
          LayoutBuilder(
            builder: (context, constraints) {
              final isMobile = constraints.maxWidth < 600;
              if (isMobile) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Predicciones IA', style: AppTextStyles.h1.copyWith(fontSize: 28)),
                    const SizedBox(height: 5),
                    Text('Machine Learning para tu negocio.', style: AppTextStyles.subtitle),
                  ],
                );
              }
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Predicciones IA', style: AppTextStyles.h1),
                  const SizedBox(height: 5),
                  Text(
                    'Anticípate al futuro con estimaciones basadas en machine learning.',
                    style: AppTextStyles.subtitle,
                  ),
                ],
              );
            },
          ),
          const SizedBox(height: 30),

          // ── TABS ──
          TabBar(
            controller: _tabController,
            labelColor: AppColors.primaryDark,
            unselectedLabelColor: AppColors.textMuted,
            indicatorColor: AppColors.accentTeal,
            isScrollable: MediaQuery.of(context).size.width < 500, // Permitir scroll horizontal en teléfonos muy estrechos
            tabs: const [
              Tab(icon: Icon(Icons.attach_money), text: 'Ventas Totales'),
              Tab(icon: Icon(Icons.inventory_2), text: 'Por Producto'),
              Tab(icon: Icon(Icons.category), text: 'Por Categoría'),
            ],
          ),
          const SizedBox(height: 20),
          
          // ── CONTENIDO TABS ──
          if (_tabController.index == 0)
            const PrediccionTab(key: ValueKey('tab0'), endpoint: '', title: 'Ventas')
          else if (_tabController.index == 1)
            const PrediccionTab(key: ValueKey('tab1'), endpoint: 'productos', title: 'Productos')
          else if (_tabController.index == 2)
            const PrediccionTab(key: ValueKey('tab2'), endpoint: 'categorias', title: 'Categorías'),
        ],
      ),
    );
  }
}
