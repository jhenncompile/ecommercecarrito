import 'dart:convert';
import 'package:flutter/material.dart';

// 1. UI Kit
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/display/app_status_pill.dart';
import '../../core/widgets/cards/app_table_card.dart';

// 2. Business Logic
import '../../dashboard/models/product_model.dart';
import '../../dashboard/repositories/product_repository.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';
import 'product_form_screen.dart';

class ProductosScreen extends StatefulWidget {
  const ProductosScreen({super.key});

  @override
  State<ProductosScreen> createState() => _ProductosScreenState();
}

class _ProductosScreenState extends State<ProductosScreen> {
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

    setState(() {
      _storeName = _formatStoreName(schemaName ?? '');
      _userName = decodedUser;
    });

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
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final productos = await _productRepository.fetchProducts();
      setState(() {
        _products = productos;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  void _abrirFormulario({ProductModel? product}) async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ProductFormScreen(product: product),
      ),
    );

    if (result == true) {
      _cargarProductos();
    }
  }

  Future<void> _confirmarEliminacion(ProductModel product) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Eliminar Producto'),
        content: Text('¿Estás seguro de que deseas eliminar "${product.nombre}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.danger),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await _productRepository.deleteProduct(product.id);
        _cargarProductos();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
        }
      }
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
          isActive: true,
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
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LayoutBuilder(
            builder: (context, constraints) {
              final isMobile = constraints.maxWidth < 600;
              if (isMobile) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Catálogo de Productos', style: AppTextStyles.h1.copyWith(fontSize: 28)),
                    const SizedBox(height: 5),
                    Text('Gestiona tus artículos y precios', style: AppTextStyles.subtitle),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      child: AppButton.add(
                        label: 'Nuevo Producto',
                        icon: Icons.add,
                        onPressed: () => _abrirFormulario(),
                      ),
                    ),
                  ],
                );
              }
              return Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Catálogo de Productos', style: AppTextStyles.h1),
                      const SizedBox(height: 5),
                      Text(
                        'Gestiona tus artículos, precios y categorías',
                        style: AppTextStyles.subtitle,
                      ),
                    ],
                  ),
                  AppButton.add(
                    label: 'Nuevo Producto',
                    icon: Icons.add,
                    onPressed: () => _abrirFormulario(),
                  ),
                ],
              );
            },
          ),
          const SizedBox(height: 30),
          if (_isLoading)
            const Center(child: CircularProgressIndicator(color: AppColors.accentTeal))
          else if (_error != null)
            Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
          else
            AppTableCard(
              title: 'Productos Registrados',
              columns: const ['Nombre', 'Categoría', 'Precio', 'Stock', 'Acciones'],
              rows: _products.map((prod) {
                return [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(prod.nombre, style: const TextStyle(fontWeight: FontWeight.bold)),
                      Text(prod.sku, style: const TextStyle(fontSize: 11, color: AppColors.textMuted)),
                    ],
                  ),
                  Text(prod.categoriaNombre ?? 'General'),
                  Text('BS. ${prod.precio.toStringAsFixed(2)}'),
                  prod.stock > 10
                      ? AppStatusPill.ok(label: '${prod.stock} un.')
                      : AppStatusPill.low(label: '${prod.stock} un.'),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.edit_outlined, color: AppColors.accentTeal, size: 20),
                        onPressed: () => _abrirFormulario(product: prod),
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.delete_outline, color: AppColors.danger, size: 20),
                        onPressed: () => _confirmarEliminacion(prod),
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                    ],
                  ),
                ];
              }).toList(),
            ),
        ],
      ),
    );
  }
}
