import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';
import 'dart:convert';

class ConfiguracionScreen extends StatefulWidget {
  const ConfiguracionScreen({super.key});

  @override
  State<ConfiguracionScreen> createState() => _ConfiguracionScreenState();
}

class _ConfiguracionScreenState extends State<ConfiguracionScreen> {
  String _storeName = 'Cargando...';
  String _userName = 'Admin';
  String _userEmail = '';
  final AuthRepository _authRepository = AuthRepository();

  @override
  void initState() {
    super.initState();
    _inicializar();
  }

  Future<void> _inicializar() async {
    final schemaName = await _authRepository.getSchemaName();
    String decodedUser = 'Admin';
    String decodedEmail = '';
    final token = await _authRepository.getAccessToken();
    if (token != null) {
      final payload = _decodeJwt(token);
      if (payload != null) {
        decodedUser = payload['full_name'] ?? payload['username'] ?? 'Admin';
        decodedEmail = payload['email'] ?? '';
      }
    }

    setState(() {
      _storeName = _formatStoreName(schemaName ?? '');
      _userName = decodedUser;
      _userEmail = decodedEmail;
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
          onTap: () => Navigator.pushReplacementNamed(context, '/predicciones'),
        ),
        AppSidebarItem(
          icon: Icons.settings,
          label: 'Configuración',
          isActive: true,
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
          Text('Configuración del Perfil', style: AppTextStyles.h1),
          const SizedBox(height: 5),
          Text(
            'Gestiona tus datos personales y de la tienda',
            style: AppTextStyles.subtitle,
          ),
          const SizedBox(height: 30),
          Container(
            padding: const EdgeInsets.all(30),
            decoration: BoxDecoration(
              color: AppColors.bgCard,
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    CircleAvatar(
                      radius: 40,
                      backgroundColor: AppColors.accentTeal.withOpacity(0.1),
                      child: const Icon(Icons.person, size: 40, color: AppColors.accentTeal),
                    ),
                    const SizedBox(width: 20),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(_userName, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.primaryDark)),
                        Text(_userEmail, style: const TextStyle(color: AppColors.textMuted)),
                      ],
                    )
                  ],
                ),
                const SizedBox(height: 30),
                const Divider(),
                const SizedBox(height: 20),
                const Text('Información de la Tienda', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 10),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Nombre de la Tienda'),
                  subtitle: Text(_storeName),
                  leading: const Icon(Icons.storefront, color: AppColors.accentTeal),
                ),
                const SizedBox(height: 30),
                AppButton.add(
                  label: 'Guardar Cambios',
                  icon: Icons.save,
                  onPressed: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
