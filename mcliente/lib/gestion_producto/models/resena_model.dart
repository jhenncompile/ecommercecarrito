class ResenaModel {
  final int id;
  final String clienteNombre;
  final int calificacion;
  final String comentario;
  final String createdAt;

  ResenaModel({
    required this.id,
    required this.clienteNombre,
    required this.calificacion,
    required this.comentario,
    required this.createdAt,
  });

  factory ResenaModel.fromJson(Map<String, dynamic> json) {
    return ResenaModel(
      id: json['id'] ?? 0,
      clienteNombre: json['cliente_nombre'] ?? 'Cliente',
      calificacion: int.tryParse(json['calificacion'].toString()) ?? 0,
      comentario: json['comentario'] ?? '',
      createdAt: (json['created_at'] ?? '').toString(),
    );
  }
}

/// Respuesta del endpoint `/resenas/producto/{id}/`
class ResenasData {
  final double promedio;
  final int total;
  final List<ResenaModel> resenas;
  final ResenaModel? miResena;
  final bool puedeResenar;

  ResenasData({
    required this.promedio,
    required this.total,
    required this.resenas,
    required this.miResena,
    required this.puedeResenar,
  });

  factory ResenasData.fromJson(Map<String, dynamic> json) {
    final resumen = (json['resumen'] as Map<String, dynamic>?) ?? {};
    final lista = (json['resenas'] as List<dynamic>?) ?? [];
    return ResenasData(
      promedio: double.tryParse(resumen['promedio']?.toString() ?? '0') ?? 0.0,
      total: int.tryParse(resumen['total']?.toString() ?? '0') ?? 0,
      resenas: lista.map((e) => ResenaModel.fromJson(e as Map<String, dynamic>)).toList(),
      miResena: json['mi_resena'] != null
          ? ResenaModel.fromJson(json['mi_resena'] as Map<String, dynamic>)
          : null,
      puedeResenar: json['puede_resenar'] ?? false,
    );
  }

  factory ResenasData.empty() =>
      ResenasData(promedio: 0, total: 0, resenas: [], miResena: null, puedeResenar: false);
}
