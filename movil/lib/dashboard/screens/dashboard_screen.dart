import 'dart:convert';
import 'package:flutter/material.dart';

// 1. UI Kit
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/cards/app_stat_card.dart';
import '../../core/widgets/display/app_status_pill.dart';
import '../../core/widgets/cards/app_table_card.dart';

// 2. Lógica de negocio
import '../models/product_model.dart';
import '../repositories/product_repository.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';
import '../../gestion_producto/screens/product_form_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<ProductModel> _products = [];
  bool _isLoading = true;
  String? _error;

  String _storeName = 'Cargando...';
  String _userName = 'Admin';

  final ProductRepository _productRepository = ProductRepository();
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

    if (mounted) {
      setState(() {
        _storeName = _formatStoreName(schemaName ?? '');
        _userName = decodedUser;
      });
    }

    await _cargarProductos();
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

  Future<void> _cargarProductos() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final productos = await _productRepository.fetchProducts();
      if (mounted) {
        setState(() {
          _products = productos;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString().replaceAll('Exception: ', '');
          _isLoading = false;
        });
      }
    }
  }

  void _abrirNuevoProducto() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ProductFormScreen()),
    );
    if (result == true) {
      _cargarProductos();
    }
  }

  double get _valorTotal => _products.fold(0, (acc, p) => acc + (p.stock * p.precio));
  int get _stockCritico => _products.where((p) => p.stock < 10).length;

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
          isActive: true,
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
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isMobile = constraints.maxWidth < 600;

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (isMobile) ...[
                Text('Bienvenido a', style: AppTextStyles.h1.copyWith(fontSize: 24)),
                Text(_storeName, style: AppTextStyles.h1.copyWith(color: AppColors.accentTeal)),
                const SizedBox(height: 5),
                Text('Resumen en tiempo real', style: AppTextStyles.subtitle),
                const SizedBox(height: 20),
                AppButton.add(
                  label: 'Nuevo Producto',
                  icon: Icons.add,
                  onPressed: _abrirNuevoProducto,
                ),
              ] else
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Bienvenido a $_storeName', style: AppTextStyles.h1),
                          const SizedBox(height: 5),
                          Text('Resumen en tiempo real de tu tienda', style: AppTextStyles.subtitle),
                        ],
                      ),
                    ),
                    AppButton.add(
                      label: 'Nuevo Producto',
                      icon: Icons.add,
                      onPressed: _abrirNuevoProducto,
                    ),
                  ],
                ),
              const SizedBox(height: 30),
              
              // Stats
              if (isMobile)
                Column(
                  children: [
                    _buildStatWrapper(
                      AppStatCard(
                        label: 'Valor Inventario',
                        value: 'BS. ${_valorTotal.toStringAsFixed(2)}',
                        changeText: 'Calculado en tiempo real',
                        isPositive: true,
                      ),
                    ),
                    const SizedBox(height: 15),
                    _buildStatWrapper(
                      AppStatCard(
                        label: 'Productos Activos',
                        value: '${_products.length}',
                        changeText: 'Sincronizado con API',
                        isPositive: true,
                      ),
                    ),
                    const SizedBox(height: 15),
                    _buildStatWrapper(
                      AppStatCard(
                        label: 'Stock Crítico',
                        value: '$_stockCritico',
                        changeText: _stockCritico > 0 ? 'Requieren atención' : 'Todo en orden',
                        isPositive: _stockCritico == 0,
                      ),
                    ),
                  ],
                )
              else
                Row(
                  children: [
                    Expanded(
                      child: AppStatCard(
                        label: 'Valor Inventario',
                        value: 'BS. ${_valorTotal.toStringAsFixed(2)}',
                        changeText: 'Calculado en tiempo real',
                        isPositive: true,
                      ),
                    ),
                    const SizedBox(width: 20),
                    Expanded(
                      child: AppStatCard(
                        label: 'Productos Activos',
                        value: '${_products.length}',
                        changeText: 'Sincronizado con API',
                        isPositive: true,
                      ),
                    ),
                    const SizedBox(width: 20),
                    Expanded(
                      child: AppStatCard(
                        label: 'Stock Crítico',
                        value: '$_stockCritico',
                        changeText: _stockCritico > 0 ? 'Requieren atención' : 'Todo en orden',
                        isPositive: _stockCritico == 0,
                      ),
                    ),
                  ],
                ),
          
          const SizedBox(height: 40),
          
          if (_isLoading)
            const Center(child: CircularProgressIndicator(color: AppColors.accentTeal))
          else if (_error != null)
            Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
          else
            AppTableCard(
              title: 'Últimos Productos Registrados',
              columns: const ['Producto', 'Categoría', 'Precio', 'Stock', 'Estado'],
              rows: _products.take(5).map((prod) {
                return [
                  Text(prod.nombre, style: const TextStyle(fontWeight: FontWeight.bold)),
                  Text(prod.categoriaNombre ?? 'General'),
                  Text('BS. ${prod.precio.toStringAsFixed(2)}'),
                  Text('${prod.stock} un.'),
                  prod.stock < 10
                      ? const AppStatusPill.low(label: 'Bajo Stock')
                      : const AppStatusPill.ok(label: 'Disponible'),
                ];
              }).toList(),
            ),
          ],
        );
      },
    ),
  );
}

  Widget _buildStatWrapper(Widget card) {
    return SizedBox(
      width: double.infinity,
      child: card,
    );
  }
}