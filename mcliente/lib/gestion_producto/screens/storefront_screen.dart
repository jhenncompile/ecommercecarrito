import 'dart:convert';
import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../models/product_model.dart';
import '../repositories/product_repository.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';
import '../../core/widgets/feedback/app_toast.dart';
import '../repositories/cart_repository.dart';
import 'product_detail_screen.dart';

class StorefrontScreen extends StatefulWidget {
  const StorefrontScreen({super.key});

  @override
  State<StorefrontScreen> createState() => _StorefrontScreenState();
}

class _StorefrontScreenState extends State<StorefrontScreen> {
  List<ProductModel> _products = [];
  List<Map<String, dynamic>> _categories = [];
  int? _selectedCategoryId;
  bool _isLoading = true;
  bool _isLoadingCats = true;
  String? _error;
  String _storeName = 'Cargando...';
  String _userName = 'Invitado';

  final ProductRepository _productRepository = ProductRepository();
  final AuthRepository _authRepository = AuthRepository();
  final CartRepository _cartRepository = CartRepository();
  int _cartItemCount = 0;

  @override
  void initState() {
    super.initState();
    _inicializar().then((_) => _loadCartCount());
  }

  Future<void> _loadCartCount() async {
    try {
      final cart = await _cartRepository.fetchActiveCart();
      setState(() {
        _cartItemCount = cart.items.fold(0, (sum, item) => sum + item.cantidad);
      });
    } catch (_) {}
  }

  Future<void> _addToCart(ProductModel product) async {
    print('[DEBUG] _addToCart iniciado para: ${product.nombre} (ID: ${product.id})');
    try {
      final cart = await _cartRepository.fetchActiveCart();
      print('[DEBUG] Carrito obtenido: ID ${cart.id}');
      await _cartRepository.addItem(cart.id, product.id);
      print('[DEBUG] Item añadido exitosamente');
      await _loadCartCount();
      if (!mounted) return;
      AppToast.showSuccess(context, '${product.nombre} añadido al carrito');
    } catch (e) {
      if (!mounted) return;
      AppToast.showError(context, 'No se pudo añadir al carrito');
    }
  }

  Future<void> _inicializar() async {
    final schemaName = await _authRepository.getSchemaName();
    String decodedUser = 'Invitado';
    final token = await _authRepository.getAccessToken();
    if (token != null) {
      final parts = token.split('.');
      if (parts.length == 3) {
        var payload = parts[1];
        while (payload.length % 4 != 0) payload += '=';
        final data = jsonDecode(utf8.decode(base64Url.decode(payload)));
        decodedUser = data['full_name'] ?? data['username'] ?? 'Invitado';
      }
    }

    setState(() {
      _storeName = schemaName?.replaceAll('_', ' ').toUpperCase() ?? 'Tienda';
      _userName = decodedUser;
    });

    await _cargarCategorias();
    await _cargarProductos();
  }

  Future<void> _cargarCategorias() async {
    try {
      final cats = await _productRepository.fetchCategories();
      setState(() {
        _categories = cats;
        _isLoadingCats = false;
      });
    } catch (_) {
      setState(() => _isLoadingCats = false);
    }
  }

  Future<void> _cargarProductos() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final productos = await _productRepository.fetchProducts(categoryId: _selectedCategoryId);
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

  @override
  Widget build(BuildContext context) {
    return AppDashboardLayout(
      brandName: 'MiQhatu',
      tenantValue: _storeName,
      userName: _userName,
      topBarTrailing: Stack(
        children: [
          IconButton(
            icon: const Icon(Icons.shopping_cart_outlined, color: AppColors.primaryDark),
            onPressed: () => Navigator.pushNamed(context, '/carrito').then((_) => _loadCartCount()),
          ),
          if (_cartItemCount > 0)
            Positioned(
              right: 8,
              top: 8,
              child: Container(
                padding: const EdgeInsets.all(2),
                decoration: const BoxDecoration(color: AppColors.danger, shape: BoxShape.circle),
                constraints: const BoxConstraints(minWidth: 16, minHeight: 16),
                child: Text('$_cartItemCount', style: const TextStyle(color: Colors.white, fontSize: 10), textAlign: TextAlign.center),
              ),
            ),
        ],
      ),
      sidebarItems: [
        AppSidebarItem(
          icon: Icons.store,
          label: 'Explorar Tiendas',
          onTap: () => Navigator.pushReplacementNamed(context, '/tiendas'),
        ),
        AppSidebarItem(
          icon: Icons.shopping_basket_outlined,
          label: 'Productos de Tienda',
          isActive: true,
          onTap: () {},
        ),
        AppSidebarItem(
          icon: Icons.shopping_bag_outlined,
          label: 'Mis Pedidos',
          onTap: () => Navigator.pushReplacementNamed(context, '/pedidos'),
        ),
        AppSidebarItem(
          icon: Icons.person_outline,
          label: 'Mi Perfil',
          onTap: () => Navigator.pushReplacementNamed(context, '/perfil'),
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
          Text('Nuestro Catálogo', style: AppTextStyles.h1),
          const SizedBox(height: 5),
          Text('Encuentra los mejores productos aquí', style: AppTextStyles.subtitle),
          const SizedBox(height: 20),
          _buildCategoryBar(),
          const SizedBox(height: 20),
          if (_isLoading)
            const Center(child: CircularProgressIndicator(color: AppColors.accentTeal))
          else if (_error != null)
            Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
          else
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: MediaQuery.of(context).size.width > 1200 ? 4 : (MediaQuery.of(context).size.width > 800 ? 3 : 2),
                crossAxisSpacing: 20,
                mainAxisSpacing: 20,
                childAspectRatio: 0.75,
              ),
              itemCount: _products.length,
              itemBuilder: (context, index) {
                final product = _products[index];
                return _buildProductCard(product);
              },
            ),
        ],
      ),
    );
  }

  Widget _buildCategoryBar() {
    if (_isLoadingCats) return const SizedBox(height: 40);
    
    return SizedBox(
      height: 45,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: _categories.length + 1,
        separatorBuilder: (context, index) => const SizedBox(width: 10),
        itemBuilder: (context, index) {
          final isAll = index == 0;
          final cat = isAll ? null : _categories[index - 1];
          final id = isAll ? null : cat!['id'];
          final name = isAll ? 'Todos' : cat!['nombre'];
          final isSelected = _selectedCategoryId == id;

          return InkWell(
            onTap: () {
              setState(() => _selectedCategoryId = id);
              _cargarProductos();
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              decoration: BoxDecoration(
                color: isSelected ? AppColors.primaryDark : AppColors.bgCard,
                borderRadius: BorderRadius.circular(25),
                border: Border.all(color: isSelected ? AppColors.primaryDark : AppColors.border),
              ),
              child: Text(
                name,
                style: TextStyle(
                  color: isSelected ? Colors.white : AppColors.textPrimary,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildProductCard(ProductModel product) {
    return InkWell(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => ProductDetailScreen(product: product)),
      ).then((refresh) {
        if (refresh == true) _loadCartCount();
      }),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.bgCard,
          borderRadius: BorderRadius.circular(15),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Hero(
                tag: 'product-${product.id}',
                child: Container(
                  width: double.infinity,
                  decoration: const BoxDecoration(
                    color: AppColors.bgSearch,
                    borderRadius: BorderRadius.vertical(top: Radius.circular(14)),
                  ),
                  child: const Icon(Icons.image_outlined, size: 50, color: AppColors.textMuted),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(product.categoriaNombre ?? 'General', style: const TextStyle(color: AppColors.accentTeal, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(product.nombre, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16), maxLines: 1, overflow: TextOverflow.ellipsis),
                  const SizedBox(height: 8),
                    Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          'BS. ${product.precio}', 
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: AppColors.primaryDark),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.add_shopping_cart, color: AppColors.accentTeal),
                        onPressed: () => _addToCart(product),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
