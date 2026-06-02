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
      imagenUrl: json['imagen_url'],
    );
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
