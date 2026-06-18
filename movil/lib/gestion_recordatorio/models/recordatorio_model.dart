// movil/lib/gestion_recordatorio/models/recordatorio_model.dart

class RecordatorioModel {
  final int id;
  final String titulo;
  final String descripcion;
  final String tipo;
  final String tipoDisplay;
  final DateTime fechaRecordatorio;
  final bool completado;
  final int? pedidoId;
  final bool notificacionEnviada;
  final bool estaVencido;

  const RecordatorioModel({
    required this.id,
    required this.titulo,
    required this.descripcion,
    required this.tipo,
    required this.tipoDisplay,
    required this.fechaRecordatorio,
    required this.completado,
    this.pedidoId,
    required this.notificacionEnviada,
    required this.estaVencido,
  });

  factory RecordatorioModel.fromJson(Map<String, dynamic> json) {
    return RecordatorioModel(
      id: json['id'] as int,
      titulo: json['titulo'] as String? ?? '',
      descripcion: json['descripcion'] as String? ?? '',
      tipo: json['tipo'] as String? ?? 'TAREA',
      tipoDisplay: json['tipo_display'] as String? ?? '',
      fechaRecordatorio: DateTime.parse(json['fecha_recordatorio'] as String),
      completado: json['completado'] as bool? ?? false,
      pedidoId: json['pedido_numero'] as int?,
      notificacionEnviada: json['notificacion_enviada'] as bool? ?? false,
      estaVencido: json['esta_vencido'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'titulo': titulo,
        'descripcion': descripcion,
        'tipo': tipo,
        'fecha_recordatorio': fechaRecordatorio.toIso8601String(),
        'completado': completado,
        if (pedidoId != null) 'pedido': pedidoId,
      };

  RecordatorioModel copyWith({
    bool? completado,
    bool? notificacionEnviada,
  }) {
    return RecordatorioModel(
      id: id,
      titulo: titulo,
      descripcion: descripcion,
      tipo: tipo,
      tipoDisplay: tipoDisplay,
      fechaRecordatorio: fechaRecordatorio,
      completado: completado ?? this.completado,
      pedidoId: pedidoId,
      notificacionEnviada: notificacionEnviada ?? this.notificacionEnviada,
      estaVencido: estaVencido,
    );
  }
}
