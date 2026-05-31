import 'package:flutter/material.dart';
import 'dart:convert';
import '../models/cliente_model.dart';
import '../repositories/cliente_repository.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/theme/app_colors.dart';
import '../../core/widgets/feedback/app_toast.dart';
import '../../core/widgets/inputs/app_input.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';

class ClientesScreen extends StatefulWidget {
  const ClientesScreen({super.key});

  @override
  State<ClientesScreen> createState() => _ClientesScreenState();
}

class _ClientesScreenState extends State<ClientesScreen> {
  String _storeName = 'Cargando...';
  String _userName = 'Admin';
  final AuthRepository _authRepository = AuthRepository();
  final ClienteRepository _clienteRepository = ClienteRepository();
  
  List<ClientModel> _clientes = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _inicializar();
    _fetchClientes();
  }

  Future<void> _fetchClientes() async {
    setState(() => _isLoading = true);
    final results = await _clienteRepository.getClientes();
    setState(() {
      _clientes = results;
      _isLoading = false;
    });
  }

  Future<void> _handleSearch(String q) async {
    setState(() {
      _isLoading = true;
    });
    final results = await _clienteRepository.searchClientes(q);
    setState(() {
      _clientes = results;
      _isLoading = false;
    });
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

  void _showRegisterDialog() {
    final nameCtrl = TextEditingController();
    final emailCtrl = TextEditingController();
    final phoneCtrl = TextEditingController();
    final nitCtrl = TextEditingController();
    final passCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Registrar Nuevo Cliente'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              AppInput(label: 'Nombre Completo', controller: nameCtrl, labelIcon: Icons.person_outline),
              const SizedBox(height: 10),
              AppInput(label: 'Correo Electrónico', controller: emailCtrl, labelIcon: Icons.email_outlined),
              const SizedBox(height: 10),
              AppInput(label: 'Teléfono', controller: phoneCtrl, labelIcon: Icons.phone_outlined),
              const SizedBox(height: 10),
              AppInput(label: 'NIT / CI', controller: nitCtrl, labelIcon: Icons.badge_outlined),
              const SizedBox(height: 10),
              AppInput(label: 'Contraseña Temporal', controller: passCtrl, labelIcon: Icons.lock_outline, obscureText: true),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          AppButton.submit(
            label: 'Registrar',
            onPressed: () async {
              final success = await _clienteRepository.registerCliente({
                'nombre': nameCtrl.text,
                'correo': emailCtrl.text,
                'telefono': phoneCtrl.text,
                'nit': nitCtrl.text,
                'contrasena': passCtrl.text,
              });
              if (success) {
                if (!mounted) return;
                Navigator.pop(context);
                AppToast.showSuccess(context, 'Cliente registrado');
                _fetchClientes();
              } else {
                if (!mounted) return;
                AppToast.showError(context, 'Error al registrar cliente');
              }
            },
          ),
        ],
      ),
    );
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
          isActive: true,
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
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Gestión de Clientes', style: AppTextStyles.h1),
              AppButton.add(
                label: 'Nuevo Cliente',
                onPressed: _showRegisterDialog,
              ),
            ],
          ),
          const SizedBox(height: 20),
          AppInput(
            label: 'Buscar cliente...',
            labelIcon: Icons.search,
            onChanged: _handleSearch,
          ),
          const SizedBox(height: 20),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: AppColors.accentTeal))
                : _clientes.isEmpty
                    ? const Center(child: Text('No se encontraron clientes'))
                    : ListView.builder(
                        itemCount: _clientes.length,
                        itemBuilder: (context, index) {
                          final cliente = _clientes[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: AppColors.accentTeal.withOpacity(0.1),
                                child: Text(cliente.nombre[0].toUpperCase(), style: const TextStyle(color: AppColors.accentTeal)),
                              ),
                              title: Text(cliente.nombre, style: const TextStyle(fontWeight: FontWeight.bold)),
                              subtitle: Text(cliente.correo),
                              trailing: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  if (cliente.nit != null) Text('NIT: ${cliente.nit}', style: const TextStyle(fontSize: 12)),
                                  if (cliente.telefono != null) Text(cliente.telefono!, style: const TextStyle(fontSize: 12)),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
