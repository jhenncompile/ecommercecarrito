import 'dart:convert';
import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/feedback/app_toast.dart';
import '../models/cart_model.dart';
import '../models/product_model.dart';
import '../repositories/cart_repository.dart';
import '../repositories/product_repository.dart';
import '../../gestion_pago/repositories/payment_repository.dart';

class CartScreen extends StatefulWidget {
  const CartScreen({super.key});

  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  CartModel? _cart;
  List<ProductModel> _recommendations = [];
  bool _isLoading = true;
  final CartRepository _cartRepository = CartRepository();
  final ProductRepository _productRepository = ProductRepository();
  final PaymentRepository _paymentRepository = PaymentRepository();

  @override
  void initState() {
    super.initState();
    _loadCart();
  }

  Future<void> _loadCart() async {
    setState(() => _isLoading = true);
    try {
      final cart = await _cartRepository.fetchActiveCart();
      setState(() {
        _cart = cart;
        _isLoading = false;
      });
      _loadRecommendations();
    } catch (e) {
      setState(() => _isLoading = false);
      AppToast.showError(context, 'Error al cargar el carrito');
    }
  }

  Future<void> _loadRecommendations() async {
    if (_cart == null || _cart!.items.isEmpty) return;
    try {
      final lastProductId = _cart!.items.last.producto.id;
      final recs = await _productRepository.fetchRecommendations(lastProductId);
      setState(() {
        _recommendations = recs;
      });
    } catch (_) {}
  }

  Future<void> _removeItem(int productId) async {
    if (_cart == null) return;
    try {
      final updatedCart = await _cartRepository.removeItem(_cart!.id, productId);
      setState(() => _cart = updatedCart);
      AppToast.showSuccess(context, 'Producto removido');
    } catch (e) {
      AppToast.showError(context, 'No se pudo remover el producto');
    }
  }

  Future<void> _processCheckout() async {
    if (_cart == null || _cart!.items.isEmpty) {
      AppToast.showInfo(context, 'Tu carrito está vacío');
      return;
    }

    try {
      AppToast.showInfo(context, 'Procesando pedido...');
      
      // Construir el payload igual que en la web
      final itemsData = _cart!.items.map((item) => {
        'producto': item.producto.id,
        'cantidad': item.cantidad,
        'precio_unitario': item.producto.precio
      }).toList();

      final pedidoResponse = await ApiClient().post(
        '${ApiConstants.mainBaseUrl}/pedidos/',
        {
          'items': itemsData,
          'total': _cart!.total
        },
        requiresAuth: true,
        includeTenantHost: true,
      );

      if (pedidoResponse.statusCode != 201 && pedidoResponse.statusCode != 200) {
        throw Exception('Error al crear el pedido en el servidor');
      }

      final pedidoData = jsonDecode(pedidoResponse.body);
      final pedidoId = pedidoData['id'];

      // Vaciar carrito local
      await _cartRepository.clearCart(_cart!.id);

      // Intentamos procesar el pago nativo
      final success = await _paymentRepository.processPaymentSheet(pedidoId);
      
      if (success) {
        AppToast.showSuccess(context, '¡Pedido realizado y pagado!');
        if (mounted) Navigator.pushReplacementNamed(context, '/pedidos');
      } else {
        AppToast.showInfo(context, 'Pago cancelado o fallido. Revisa Mis Pedidos.');
        if (mounted) Navigator.pushReplacementNamed(context, '/pedidos');
      }
    } catch (e) {
      AppToast.showError(context, 'Error al procesar el pago: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppDashboardLayout(
      brandName: 'MiQhatu',
      userName: 'Cliente',
      sidebarItems: [
        AppSidebarItem(
          icon: Icons.store,
          label: 'Explorar Tiendas',
          onTap: () => Navigator.pushReplacementNamed(context, '/tiendas'),
        ),
        AppSidebarItem(
          icon: Icons.storefront,
          label: 'Catálogo de Tienda',
          onTap: () => Navigator.pushReplacementNamed(context, '/tienda'),
        ),
        AppSidebarItem(
          icon: Icons.shopping_bag_outlined,
          label: 'Mis Pedidos',
          onTap: () => Navigator.pushReplacementNamed(context, '/pedidos'),
        ),
        AppSidebarItem(
          icon: Icons.logout,
          label: 'Salir',
          isLogout: true,
          onTap: () => Navigator.pushReplacementNamed(context, '/login'),
        ),
      ],
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Tu Carrito', style: AppTextStyles.h1),
          const SizedBox(height: 30),
          if (_isLoading)
            const Center(child: CircularProgressIndicator(color: AppColors.accentTeal))
          else if (_cart == null || _cart!.items.isEmpty)
            _buildEmptyCart()
          else
            _buildCartContent(),
        ],
      ),
    );
  }

  Widget _buildEmptyCart() {
    return Center(
      child: Column(
        children: [
          const Icon(Icons.shopping_cart_outlined, size: 80, color: AppColors.textMuted),
          const SizedBox(height: 20),
          const Text('Tu carrito está vacío', style: TextStyle(fontSize: 18, color: AppColors.textMuted)),
          const SizedBox(height: 30),
          AppButton.primary(
            label: 'Ir a comprar',
            onPressed: () => Navigator.pushReplacementNamed(context, '/tienda'),
          ),
        ],
      ),
    );
  }

  Widget _buildCartContent() {
    return Column(
      children: [
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _cart!.items.length,
          separatorBuilder: (context, index) => const Divider(),
          itemBuilder: (context, index) {
            final item = _cart!.items[index];
            return ListTile(
              leading: Container(
                width: 50, height: 50,
                decoration: BoxDecoration(color: AppColors.bgSearch, borderRadius: BorderRadius.circular(8)),
                child: const Icon(Icons.image_outlined, color: AppColors.textMuted),
              ),
              title: Text(item.producto.nombre, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('${item.cantidad} x BS. ${item.producto.precio}'),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('BS. ${item.subtotal}', style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primaryDark)),
                  const SizedBox(width: 10),
                  IconButton(
                    icon: const Icon(Icons.delete_outline, color: AppColors.danger),
                    onPressed: () => _removeItem(item.producto.id),
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 40),
        Container(
          padding: const EdgeInsets.all(25),
          decoration: BoxDecoration(
            color: AppColors.bgCard,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Expanded(
                    child: Text('Total a pagar:', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  ),
                  Text('BS. ${_cart!.total}', style: AppTextStyles.h2.copyWith(color: AppColors.accentTeal)),
                ],
              ),
              const SizedBox(height: 25),
              AppButton.submit(
                label: 'Proceder al Pago',
                onPressed: _processCheckout,
              ),
            ],
          ),
        ),
        if (_recommendations.isNotEmpty) _buildRecommendationsSection(),
        const SizedBox(height: 40),
      ],
    );
  }

  Widget _buildRecommendationsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 40),
        const Text('Te podría interesar', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 15),
        SizedBox(
          height: 180,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: _recommendations.length,
            separatorBuilder: (context, index) => const SizedBox(width: 15),
            itemBuilder: (context, index) {
              final rec = _recommendations[index];
              return Container(
                width: 140,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.bgCard,
                  borderRadius: BorderRadius.circular(15),
                  border: Border.all(color: AppColors.border),
                ),
                child: Column(
                  children: [
                    Expanded(child: Icon(Icons.shopping_bag_outlined, color: AppColors.accentTeal.withOpacity(0.5), size: 40)),
                    Text(rec.nombre, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12), maxLines: 2, textAlign: TextAlign.center),
                    const SizedBox(height: 5),
                    Text('BS. ${rec.precio}', style: const TextStyle(color: AppColors.accentTeal, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 5),
                    InkWell(
                      onTap: () async {
                        await _cartRepository.addItem(_cart!.id, rec.id);
                        _loadCart();
                      },
                      child: const Text('Añadir', style: TextStyle(color: AppColors.primaryDark, fontSize: 11, fontWeight: FontWeight.bold)),
                    )
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
