class ProductModel {
  final int id;
  final String nombre;
  final String descripcion;
  final double precio;
  final int stock;
  final String sku;
  final int? categoria;
  final String? categoriaNombre;

  // Preventa (Reservas)
  final bool isPreorder;
  final String? estimatedArrivalDate;
  final double preorderDiscountPercentage;

  ProductModel({
    required this.id,
    required this.nombre,
    required this.descripcion,
    required this.precio,
    required this.stock,
    this.sku = '',
    this.categoria,
    this.categoriaNombre,
    this.isPreorder = false,
    this.estimatedArrivalDate,
    this.preorderDiscountPercentage = 0.0,
  });

  factory ProductModel.fromJson(Map<String, dynamic> json) {
    return ProductModel(
      id: json['id'] ?? 0,
      nombre: json['nombre'] ?? '',
      descripcion: json['descripcion'] ?? '',
      precio: double.tryParse(json['precio'].toString()) ?? 0.0,
      stock: int.tryParse(json['stock'].toString()) ?? 0,
      sku: json['sku'] ?? '',
      categoria: json['categoria'],
      categoriaNombre: json['categoria_detail']?['nombre'],
      isPreorder: json['is_preorder'] ?? false,
      estimatedArrivalDate: json['estimated_arrival_date'],
      preorderDiscountPercentage: double.tryParse(json['preorder_discount_percentage']?.toString() ?? '0') ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'descripcion': descripcion,
        'precio': precio.toString(),
        'stock': stock,
        'sku': sku,
        'categoria': categoria,
        'is_preorder': isPreorder,
        'estimated_arrival_date': estimatedArrivalDate,
        'preorder_discount_percentage': preorderDiscountPercentage,
      };
}