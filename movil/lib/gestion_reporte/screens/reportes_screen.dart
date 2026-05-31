import 'dart:convert';
import 'package:flutter/material.dart';

// UI Kit
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';

// Business Logic
import '../../gestion_usuario/repositories/auth_repository.dart';

// Pestañas
import '../widgets/reporte_basico_tab.dart';
import '../widgets/reporte_voz_tab.dart';

class ReportesScreen extends StatefulWidget {
  const ReportesScreen({super.key});

  @override
  State<ReportesScreen> createState() => _ReportesScreenState();
}

class _ReportesScreenState extends State<ReportesScreen> {
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
    return DefaultTabController(
      length: 2,
      child: AppDashboardLayout(
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
            isActive: true,
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
                      Text('Reportes & Análisis', style: AppTextStyles.h1.copyWith(fontSize: 28)),
                      const SizedBox(height: 5),
                      Text('Inteligencia de negocio con IA.', style: AppTextStyles.subtitle),
                    ],
                  );
                }
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Reportes & Análisis', style: AppTextStyles.h1),
                    const SizedBox(height: 5),
                    Text(
                      'Explora métricas, crea reportes y consulta con tu voz',
                      style: AppTextStyles.subtitle,
                    ),
                  ],
                );
              },
            ),
            const SizedBox(height: 30),

            // ── TABS ──
            const TabBar(
              labelColor: AppColors.primaryDark,
              unselectedLabelColor: AppColors.textMuted,
              indicatorColor: AppColors.accentTeal,
              tabs: [
                Tab(icon: Icon(Icons.bar_chart), text: 'Básicos'),
                Tab(icon: Icon(Icons.mic), text: 'Voz (IA)'),
              ],
            ),
            const SizedBox(height: 20),
            
            // ── CONTENIDO TABS ──
            const SizedBox(height: 20),
            SizedBox(
              height: 600, // Alto fijo para que el TabBarView pueda scrollear o ajustarse
              child: TabBarView(
                children: [
                  SingleChildScrollView(child: ReporteBasicoTab()),
                  SingleChildScrollView(child: ReporteVozTab()),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

