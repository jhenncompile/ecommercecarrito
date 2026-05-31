import 'dart:convert';
import 'package:flutter/material.dart';

// UI Kit
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/display/app_status_pill.dart';
import '../../core/widgets/cards/app_table_card.dart';
import '../../core/widgets/cards/app_stat_card.dart';

// Business Logic
import '../../dashboard/models/product_model.dart';
import '../../dashboard/repositories/product_repository.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';

class InventarioScreen extends StatefulWidget {
  const InventarioScreen({super.key});

  @override
  State<InventarioScreen> createState() => _InventarioScreenState();
}

class _InventarioScreenState extends State<InventarioScreen> {
  List<ProductModel> _products = [];
  bool _isLoading = true;
  String? _error;
  int? _updatingId;

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

  Future<void> _adjustStock(ProductModel product, int delta, {bool isAbsolute = false}) async {
    final newStock = isAbsolute ? delta : (product.stock + delta);
    if (newStock < 0) return;

    setState(() => _updatingId = product.id);

    try {
      await _productRepository.adjustStock(product.id, newStock);
      await _cargarProductos();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      setState(() => _updatingId = null);
    }
  }

  void _showManualAdjustment(ProductModel product) {
    final controller = TextEditingController(text: product.stock.toString());
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Ajuste Manual: ${product.nombre}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Ingresa el nuevo stock total para este producto.'),
            const SizedBox(height: 15),
            TextField(
              controller: controller,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Nuevo Stock', border: OutlineInputBorder()),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () {
              final val = int.tryParse(controller.text);
              if (val != null) {
                Navigator.pop(context);
                _adjustStock(product, val, isAbsolute: true);
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.accentTeal),
            child: const Text('Aplicar'),
          ),
        ],
      ),
    );
  }

  double get _valorTotal => _products.fold(0, (acc, p) => acc + (p.stock * p.precio));
  int get _stockBajo => _products.where((p) => p.stock > 0 && p.stock < 10).length;
  int get _agotados => _products.where((p) => p.stock <= 0).length;

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
          isActive: true,
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
                Text('Inventario', style: AppTextStyles.h1.copyWith(fontSize: 28)),
                const SizedBox(height: 5),
                Text('Control de stock y valoración', style: AppTextStyles.subtitle),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  child: AppButton.add(
                    label: 'Sincronizar',
                    icon: Icons.refresh,
                    onPressed: _cargarProductos,
                  ),
                ),
              ] else
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Gestión de Inventario', style: AppTextStyles.h1),
                        const SizedBox(height: 5),
                        Text(
                          'Control de stock y valoración de productos',
                          style: AppTextStyles.subtitle,
                        ),
                      ],
                    ),
                    AppButton.add(
                      label: 'Sincronizar',
                      icon: Icons.refresh,
                      onPressed: _cargarProductos,
                    ),
                  ],
                ),
              const SizedBox(height: 30),
              
              if (isMobile)
                Column(
                  children: [
                    _buildStatWrapper(
                      AppStatCard(
                        label: 'Valor Inventario',
                        value: 'BS. ${_valorTotal.toStringAsFixed(2)}',
                        changeText: 'Total acumulado',
                        isPositive: true,
                      ),
                    ),
                    const SizedBox(height: 15),
                    _buildStatWrapper(
                      AppStatCard(
                        label: 'Stock Bajo',
                        value: '$_stockBajo',
                        changeText: 'Requieren atención',
                        isPositive: _stockBajo == 0,
                      ),
                    ),
                    const SizedBox(height: 15),
                    _buildStatWrapper(
                      AppStatCard(
                        label: 'Agotados',
                        value: '$_agotados',
                        changeText: 'Sin unidades',
                        isPositive: _agotados == 0,
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
                        changeText: 'Total acumulado',
                        isPositive: true,
                      ),
                    ),
                    const SizedBox(width: 20),
                    Expanded(
                      child: AppStatCard(
                        label: 'Stock Bajo',
                        value: '$_stockBajo',
                        changeText: 'Requieren atención',
                        isPositive: _stockBajo == 0,
                      ),
                    ),
                    const SizedBox(width: 20),
                    Expanded(
                      child: AppStatCard(
                        label: 'Agotados',
                        value: '$_agotados',
                        changeText: 'Sin unidades',
                        isPositive: _agotados == 0,
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
              title: 'Ajuste de Stock',
              columns: const ['Producto', 'Stock Actual', 'Ajuste Rápido', 'Valor Total'],
              rows: _products.map((prod) {
                final isUpdating = _updatingId == prod.id;
                return [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(prod.nombre, style: const TextStyle(fontWeight: FontWeight.bold)),
                      Text(prod.sku, style: const TextStyle(fontSize: 11, color: AppColors.textMuted)),
                    ],
                  ),
                  prod.stock <= 0 ? const AppStatusPill.low(label: 'Agotado') : Text('${prod.stock} un.'),
                  isUpdating
                      ? const SizedBox(width: 100, child: LinearProgressIndicator(color: AppColors.accentTeal))
                      : Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            _buildAdjustBtn(Icons.remove, () => _adjustStock(prod, -1)),
                            const SizedBox(width: 8),
                            _buildAdjustBtn(Icons.add, () => _adjustStock(prod, 1)),
                            const SizedBox(width: 8),
                            _buildAdjustBtn(Icons.edit, () => _showManualAdjustment(prod), color: AppColors.textMuted),
                          ],
                        ),
                  Text('BS. ${(prod.stock * prod.precio).toStringAsFixed(2)}'),
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

  Widget _buildAdjustBtn(IconData icon, VoidCallback onTap, {Color color = AppColors.accentTeal}) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: IconButton(
        icon: Icon(icon, size: 16, color: color),
        onPressed: onTap,
        padding: EdgeInsets.zero,
      ),
    );
  }
}
