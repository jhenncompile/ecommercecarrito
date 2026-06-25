class PedidoItem {
  final int id;
  final int productoId;
  final String productoNombre;
  final String productoPrecio;
  final int cantidad;
  final String subtotal;

  PedidoItem({
    required this.id,
    required this.productoId,
    required this.productoNombre,
    required this.productoPrecio,
    required this.cantidad,
    required this.subtotal,
  });

  factory PedidoItem.fromJson(Map<String, dynamic> json) {
    return PedidoItem(
      id: json['id'] ?? 0,
      productoId: json['producto'] is Map ? (json['producto']['id'] ?? 0) : (json['producto'] ?? 0),
      productoNombre: json['producto_nombre'] ?? '',
      productoPrecio: json['producto_precio']?.toString() ?? '0.00',
      cantidad: json['cantidad'] ?? 0,
      subtotal: json['subtotal']?.toString() ?? '0.00',
    );
  }
}

class Pedido {
  final int id;
  final int carritoId;
  final String clienteNombre;
  final String clienteEmail;
  final String estado;
  final String fechaCreacion;
  final String? observaciones;
  final String totalPedido;
  final int cantidadItems;
  final List<PedidoItem> items;

  Pedido({
    required this.id,
    required this.carritoId,
    required this.clienteNombre,
    required this.clienteEmail,
    required this.estado,
    required this.fechaCreacion,
    this.observaciones,
    required this.totalPedido,
    required this.cantidadItems,
    required this.items,
  });

  factory Pedido.fromJson(Map<String, dynamic> json) {
    var itemsList = json['items'] as List? ?? [];
    List<PedidoItem> itemsObj = itemsList.map((i) => PedidoItem.fromJson(i)).toList();

    return Pedido(
      id: json['id'] ?? 0,
      carritoId: json['carrito_id'] ?? 0,
      clienteNombre: json['cliente_nombre'] ?? 'Desconocido',
      clienteEmail: json['cliente_email'] ?? '',
      estado: json['estado'] ?? 'PENDIENTE',
      fechaCreacion: json['fecha_creacion'] ?? '',
      observaciones: json['observaciones'],
      totalPedido: json['total_pedido']?.toString() ?? '0.00',
      cantidadItems: json['cantidad_items'] ?? 0,
      items: itemsObj,
    );
  }
}
