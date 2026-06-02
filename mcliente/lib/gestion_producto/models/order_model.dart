import 'cart_model.dart';

class OrderModel {
  final int id;
  final String numero;
  final String estado;
  final double total;
  final DateTime fecha;
  final List<CartItemModel>? items;
  final String? tenantName;
  final String? schemaName;

  OrderModel({
    required this.id,
    required this.numero,
    required this.estado,
    required this.total,
    required this.fecha,
    this.items,
    this.tenantName,
    this.schemaName,
  });

  factory OrderModel.fromJson(Map<String, dynamic> json) {
    return OrderModel(
      id: json['id'],
      numero: json['numero_pedido'] ?? json['numero'] ?? 'PED-${json['id']}',
      estado: json['estado'] ?? 'PENDIENTE',
      total: double.parse((json['total_pedido'] ?? json['total'] ?? 0).toString()),
      fecha: DateTime.parse(json['fecha_creacion'] ?? json['created_at'] ?? DateTime.now().toIso8601String()),
      tenantName: json['tenant_name'],
      schemaName: json['subdominio'] ?? json['schema_name'],
      items: json['items'] != null
          ? (json['items'] as List).map((i) => CartItemModel.fromJson(i)).toList()
          : null,
    );
  }
}
