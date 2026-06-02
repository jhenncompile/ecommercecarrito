import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/feedback/app_toast.dart';
import '../models/product_model.dart';
import '../repositories/cart_repository.dart';

class ProductDetailScreen extends StatefulWidget {
  final ProductModel product;

  const ProductDetailScreen({super.key, required this.product});

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  final CartRepository _cartRepository = CartRepository();
  bool _isAdding = false;

  Future<void> _addToCart() async {
    setState(() => _isAdding = true);
    try {
      final cart = await _cartRepository.fetchActiveCart();
      await _cartRepository.addItem(cart.id, widget.product.id);
      if (!mounted) return;
      AppToast.showSuccess(context, '¡${widget.product.nombre} añadido!');
      Navigator.pop(context, true); // Retornar true para indicar que el carrito cambió
    } catch (e) {
      if (!mounted) return;
      AppToast.showError(context, 'Error al añadir al carrito');
    } finally {
      if (mounted) setState(() => _isAdding = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: CustomScrollView(
        slivers: [
          _buildAppBar(context),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(),
                  const SizedBox(height: 24),
                  _buildPriceSection(),
                  const SizedBox(height: 24),
                  _buildDescription(),
                  const SizedBox(height: 32),
                  _buildMetaInfo(),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: _buildBottomAction(),
    );
  }

  Widget _buildAppBar(BuildContext context) {
    return SliverAppBar(
      expandedHeight: 400,
      pinned: true,
      backgroundColor: AppColors.primaryDark,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back, color: Colors.white),
        onPressed: () => Navigator.pop(context),
      ),
      flexibleSpace: FlexibleSpaceBar(
        background: Hero(
          tag: 'product-${widget.product.id}',
          child: Container(
            color: AppColors.bgSearch,
            child: widget.product.imagenUrl != null && widget.product.imagenUrl!.isNotEmpty
                ? Image.network(widget.product.imagenUrl!, fit: BoxFit.cover)
                : const Center(
                    child: Icon(Icons.image_outlined, size: 100, color: AppColors.textMuted),
                  ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: AppColors.accentTeal.withOpacity(0.1),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            widget.product.categoriaNombre?.toUpperCase() ?? 'GENERAL',
            style: const TextStyle(
              color: AppColors.accentTeal,
              fontWeight: FontWeight.bold,
              fontSize: 12,
              letterSpacing: 1.2,
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text(widget.product.nombre, style: AppTextStyles.h1),
      ],
    );
  }

  Widget _buildPriceSection() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Precio total', style: TextStyle(color: AppColors.textMuted, fontSize: 14)),
            const SizedBox(height: 4),
            Text(
              'BS. ${widget.product.precio}',
              style: const TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.w900,
                color: AppColors.primaryDark,
                letterSpacing: -1,
              ),
            ),
          ],
        ),
        if (widget.product.stock < 5 && widget.product.stock > 0)
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.danger.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              '🔥 ¡Pocas unidades!',
              style: TextStyle(color: AppColors.danger, fontWeight: FontWeight.bold, fontSize: 12),
            ),
          ),
      ],
    );
  }

  Widget _buildDescription() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Descripción', style: AppTextStyles.h3),
        const SizedBox(height: 12),
        Text(
          widget.product.descripcion.isNotEmpty 
              ? widget.product.descripcion 
              : 'Este producto no cuenta con una descripción detallada en este momento.',
          style: const TextStyle(
            fontSize: 16,
            color: AppColors.textPrimary,
            height: 1.6,
          ),
        ),
      ],
    );
  }

  Widget _buildMetaInfo() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.bgSearch,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          _buildMetaRow('Disponibilidad', widget.product.stock > 0 ? '${widget.product.stock} unidades' : 'Agotado', 
              widget.product.stock > 0 ? AppColors.accentTeal : AppColors.danger),
          const Divider(height: 30),
          _buildMetaRow('Código SKU', widget.product.sku.isNotEmpty ? widget.product.sku : '#PRD-${widget.product.id}', AppColors.textPrimary),
        ],
      ),
    );
  }

  Widget _buildMetaRow(String label, String value, Color valueColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: AppColors.textMuted)),
        Text(value, style: TextStyle(fontWeight: FontWeight.bold, color: valueColor)),
      ],
    );
  }

  Widget _buildBottomAction() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, -5)),
        ],
      ),
      child: AppButton.primary(
        label: _isAdding ? 'Añadiendo...' : 'Agregar al carrito',
        onPressed: widget.product.stock > 0 ? _addToCart : null,
      ),
    );
  }
}
