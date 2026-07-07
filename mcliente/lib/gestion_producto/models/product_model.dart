import '../../core/constants/api_constants.dart';

class ProductModel {
  final int id;
  final String nombre;
  final String descripcion;
  final double precio;
  final int stock;
  final String sku;
  final int? categoria;
  final String? categoriaNombre;
  final String? imagenUrl;

  // Preventa (Reservas) + precios calculados en el backend
  final bool isPreorder;
  final String? estimatedArrivalDate;
  final double preorderDiscountPercentage;
  final double precioOriginal;
  final double precioFinal;
  final bool enPreventa;

  ProductModel({
    required this.id,
    required this.nombre,
    required this.descripcion,
    required this.precio,
    required this.stock,
    this.sku = '',
    this.categoria,
    this.categoriaNombre,
    this.imagenUrl,
    this.isPreorder = false,
    this.estimatedArrivalDate,
    this.preorderDiscountPercentage = 0.0,
    double? precioOriginal,
    double? precioFinal,
    this.enPreventa = false,
  })  : precioOriginal = precioOriginal ?? precio,
        precioFinal = precioFinal ?? precio;

  factory ProductModel.fromJson(Map<String, dynamic> json) {
    final precio = double.tryParse(json['precio'].toString()) ?? 0.0;
    return ProductModel(
      id: json['id'] ?? 0,
      nombre: json['nombre'] ?? '',
      descripcion: json['descripcion'] ?? '',
      precio: precio,
      stock: int.tryParse(json['stock'].toString()) ?? 0,
      sku: json['sku'] ?? '',
      categoria: json['categoria'],
      categoriaNombre: json['categoria_detail']?['nombre'] ?? json['categoria_nombre'],
      imagenUrl: _resolveImageUrl(json['imagen_url']),
      isPreorder: json['is_preorder'] ?? false,
      estimatedArrivalDate: json['estimated_arrival_date'],
      preorderDiscountPercentage: double.tryParse(json['preorder_discount_percentage']?.toString() ?? '0') ?? 0.0,
      precioOriginal: double.tryParse(json['precio_original']?.toString() ?? '') ?? precio,
      precioFinal: double.tryParse(json['precio_final']?.toString() ?? '') ?? precio,
      enPreventa: json['en_preventa'] ?? (json['is_preorder'] ?? false),
    );
  }

  // Indica si el precio final es menor al original (descuento aplicado)
  bool get tieneDescuento => precioFinal < precioOriginal;

  static String? _resolveImageUrl(String? url) {
    if (url == null || url.isEmpty) return null;
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    return 'http://${ApiConstants.vpsIp}:${ApiConstants.djangoPort}$url'; // Fallback para URLs relativas
  }

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'descripcion': descripcion,
        'precio': precio.toString(),
        'stock': stock,
        'sku': sku,
        'categoria': categoria,
      };
}
