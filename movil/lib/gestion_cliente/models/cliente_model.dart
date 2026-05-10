class ClientModel {
  final int id;
  final String nombre;
  final String correo;
  final String? telefono;
  final String? nit;
  final String? fechaRegistro;

  ClientModel({
    required this.id,
    required this.nombre,
    required this.correo,
    this.telefono,
    this.nit,
    this.fechaRegistro,
  });

  factory ClientModel.fromJson(Map<String, dynamic> json) {
    return ClientModel(
      id: json['id'],
      nombre: json['nombre'],
      correo: json['correo'],
      telefono: json['telefono'],
      nit: json['nit'],
      fechaRegistro: json['fecha_registro'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nombre': nombre,
      'correo': correo,
      'telefono': telefono,
      'nit': nit,
    };
  }
}
