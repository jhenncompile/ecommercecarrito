import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/feedback/app_toast.dart';
import '../models/product_model.dart';
import '../models/resena_model.dart';
import '../repositories/cart_repository.dart';
import '../repositories/resena_repository.dart';
import '../repositories/restock_repository.dart';

class ProductDetailScreen extends StatefulWidget {
  final ProductModel product;

  const ProductDetailScreen({super.key, required this.product});

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  final CartRepository _cartRepository = CartRepository();
  final RestockRepository _restockRepository = RestockRepository();
  bool _isAdding = false;
  bool _solicitandoRestock = false;

  Future<void> _solicitarRestock() async {
    setState(() => _solicitandoRestock = true);
    try {
      final msg = await _restockRepository.solicitar(widget.product.id);
      if (!mounted) return;
      AppToast.showSuccess(context, msg);
    } catch (e) {
      if (!mounted) return;
      AppToast.showError(context, e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _solicitandoRestock = false);
    }
  }

  // Reseñas y Calificaciones (CU-27)
  final ResenaRepository _resenaRepository = ResenaRepository();
  ResenasData? _resenas;
  bool _loadingResenas = true;
  int _miCalificacion = 0;
  final TextEditingController _comentarioCtrl = TextEditingController();
  bool _enviandoResena = false;

  @override
  void initState() {
    super.initState();
    _cargarResenas();
  }

  @override
  void dispose() {
    _comentarioCtrl.dispose();
    super.dispose();
  }

  Future<void> _cargarResenas() async {
    setState(() => _loadingResenas = true);
    try {
      final data = await _resenaRepository.fetchResenas(widget.product.id);
      if (!mounted) return;
      setState(() {
        _resenas = data;
        _miCalificacion = data.miResena?.calificacion ?? 0;
        if (data.miResena != null) _comentarioCtrl.text = data.miResena!.comentario;
        _loadingResenas = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _resenas = ResenasData.empty();
        _loadingResenas = false;
      });
    }
  }

  Future<void> _enviarResena() async {
    if (_miCalificacion < 1) {
      AppToast.showInfo(context, 'Selecciona una calificación (1 a 5 estrellas).');
      return;
    }
    setState(() => _enviandoResena = true);
    try {
      await _resenaRepository.enviarResena(widget.product.id, _miCalificacion, _comentarioCtrl.text.trim());
      if (!mounted) return;
      AppToast.showSuccess(context, '¡Gracias por tu reseña!');
      await _cargarResenas();
    } catch (e) {
      if (!mounted) return;
      AppToast.showError(context, e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _enviandoResena = false);
    }
  }

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
                  const SizedBox(height: 32),
                  _buildResenasSection(),
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
        if (widget.product.enPreventa)
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFF7C3AED),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text(
              'PRE-VENTA',
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 1.2),
            ),
          ),
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
            if (widget.product.tieneDescuento)
              Text(
                'BS. ${widget.product.precioOriginal.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 16,
                  color: AppColors.textMuted,
                  decoration: TextDecoration.lineThrough,
                ),
              ),
            Text(
              'BS. ${widget.product.precioFinal.toStringAsFixed(2)}',
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
          _buildMetaRow('Disponibilidad', widget.product.stock > 0 ? '${widget.product.stock} unidades' : (widget.product.enPreventa ? 'En preventa' : 'Agotado'),
              widget.product.stock > 0 ? AppColors.accentTeal : AppColors.danger),
          if (widget.product.enPreventa && (widget.product.estimatedArrivalDate?.isNotEmpty ?? false)) ...[
            const Divider(height: 30),
            _buildMetaRow('Llegada estimada', widget.product.estimatedArrivalDate!, AppColors.primaryDark),
          ],
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

  static const Color _starColor = Color(0xFFF59E0B);

  Widget _buildStars(double rating, {double size = 16}) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(5, (i) {
        IconData icon;
        if (rating >= i + 1) {
          icon = Icons.star;
        } else if (rating >= i + 0.5) {
          icon = Icons.star_half;
        } else {
          icon = Icons.star_border;
        }
        return Icon(icon, size: size, color: _starColor);
      }),
    );
  }

  Widget _buildResenasSection() {
    final data = _resenas;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text('Reseñas', style: AppTextStyles.h3),
            const SizedBox(width: 10),
            if (data != null && data.total > 0) ...[
              _buildStars(data.promedio, size: 18),
              const SizedBox(width: 6),
              Text('${data.promedio.toStringAsFixed(1)} (${data.total})',
                  style: const TextStyle(color: AppColors.textMuted, fontWeight: FontWeight.bold)),
            ],
          ],
        ),
        const SizedBox(height: 16),
        if (_loadingResenas)
          const Center(child: Padding(padding: EdgeInsets.all(12), child: CircularProgressIndicator(color: AppColors.accentTeal)))
        else ...[
          if (data != null && data.puedeResenar) ...[
            _buildResenaForm(data),
            const SizedBox(height: 20),
          ],
          if (data == null || data.resenas.isEmpty)
            const Text('Aún no hay reseñas para este producto.', style: TextStyle(color: AppColors.textMuted))
          else
            ...data.resenas.map(_buildResenaItem),
        ],
      ],
    );
  }

  Widget _buildStarSelector() {
    return Row(
      children: List.generate(5, (i) {
        final filled = i < _miCalificacion;
        return IconButton(
          padding: const EdgeInsets.symmetric(horizontal: 2),
          constraints: const BoxConstraints(),
          icon: Icon(filled ? Icons.star : Icons.star_border, color: _starColor, size: 32),
          onPressed: () => setState(() => _miCalificacion = i + 1),
        );
      }),
    );
  }

  Widget _buildResenaForm(ResenasData data) {
    final yaReseno = data.miResena != null;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.bgSearch,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(yaReseno ? 'Editar tu reseña' : 'Deja tu reseña',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),
          _buildStarSelector(),
          const SizedBox(height: 12),
          TextField(
            controller: _comentarioCtrl,
            maxLines: 3,
            decoration: InputDecoration(
              hintText: 'Cuéntanos tu experiencia (opcional)',
              filled: true,
              fillColor: Colors.white,
              contentPadding: const EdgeInsets.all(12),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: AppColors.border)),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primaryDark,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: _enviandoResena ? null : _enviarResena,
              child: Text(_enviandoResena ? 'Enviando...' : (yaReseno ? 'Actualizar reseña' : 'Enviar reseña'),
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResenaItem(ResenaModel r) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(child: Text(r.clienteNombre, style: const TextStyle(fontWeight: FontWeight.bold))),
              _buildStars(r.calificacion.toDouble(), size: 14),
            ],
          ),
          if (r.comentario.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(r.comentario, style: const TextStyle(color: AppColors.textPrimary, height: 1.4)),
          ],
          if (r.createdAt.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(r.createdAt.length >= 10 ? r.createdAt.substring(0, 10) : r.createdAt,
                style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
          ],
        ],
      ),
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
      child: (widget.product.stock <= 0 && !widget.product.enPreventa)
          ? AppButton.primary(
              label: _solicitandoRestock ? 'Enviando...' : 'Avísame cuando vuelva a haber stock',
              onPressed: _solicitandoRestock ? null : _solicitarRestock,
            )
          : AppButton.primary(
              label: _isAdding
                  ? 'Añadiendo...'
                  : (widget.product.enPreventa ? 'Reservar con Descuento' : 'Agregar al carrito'),
              onPressed: (widget.product.enPreventa || widget.product.stock > 0) ? _addToCart : null,
            ),
    );
  }
}
