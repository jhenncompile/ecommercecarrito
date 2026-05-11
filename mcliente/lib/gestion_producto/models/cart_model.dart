import 'product_model.dart';

class CartItemModel {
  final int? id;
  final ProductModel producto;
  final int cantidad;
  final double subtotal;

  CartItemModel({
    this.id,
    required this.producto,
    required this.cantidad,
    required this.subtotal,
  });

  factory CartItemModel.fromJson(Map<String, dynamic> json) {
    // Si 'producto' viene como ID (int), creamos un modelo básico
    // Si viene como Map, usamos el fromJson normal
    ProductModel product;
    if (json['producto'] is int) {
      product = ProductModel(
        id: json['producto'],
        nombre: json['producto_nombre'] ?? 'Producto #${json['producto']}',
        descripcion: '',
        precio: double.tryParse(json['producto_precio']?.toString() ?? '0') ?? 0.0,
        stock: 0,
      );
    } else {
      product = ProductModel.fromJson(json['producto'] as Map<String, dynamic>);
    }

    return CartItemModel(
      id: json['id'],
      producto: product,
      cantidad: json['cantidad'] ?? 1,
      subtotal: double.tryParse(json['subtotal']?.toString() ?? '0') ?? 0.0,
    );
  }
}

class CartModel {
  final int id;
  final List<CartItemModel> items;
  final double total;
  final String estado;

  CartModel({
    required this.id,
    required this.items,
    required this.total,
    required this.estado,
  });

  factory CartModel.fromJson(Map<String, dynamic> json) {
    print('[DEBUG] Parsing Cart JSON: $json');
    var itemsList = (json['items'] as List?) ?? [];
    
    // El backend puede enviar total_carrito o total
    final totalValue = json['total'] ?? json['total_carrito'] ?? 0.0;
    
    return CartModel(
      id: json['id'] ?? 0,
      items: itemsList.map((i) => CartItemModel.fromJson(i as Map<String, dynamic>)).toList(),
      total: double.tryParse(totalValue.toString()) ?? 0.0,
      estado: json['estado'] ?? 'ABIERTO',
    );
  }
}
