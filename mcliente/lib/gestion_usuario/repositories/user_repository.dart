import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';

class UserModel {
  final int id;
  final String nombre;
  final String correo;
  final String? telefono;
  final String? nit;

  UserModel({
    required this.id,
    required this.nombre,
    required this.correo,
    this.telefono,
    this.nit,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      nombre: json['nombre'],
      correo: json['correo'],
      telefono: json['telefono'],
      nit: json['nit'],
    );
  }
}

class UserRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<UserModel> fetchProfile() async {
    // Para simplificar, si no tenemos el ID, podemos tener un endpoint /me/
    // O extraerlo del token. El backend de clientes suele tener el ID en el payload.
    // Vamos a intentar obtener el ID del token primero.
    final token = await _storage.getAccessToken();
    if (token == null) throw Exception('No autenticado');

    final url = '${ApiConstants.mainBaseUrl}/clientes/perfil/';
    final response = await _apiClient.get(url, requiresAuth: true);

    if (response.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Error al cargar perfil');
    }
  }

  Future<UserModel> updateProfile(int id, Map<String, dynamic> data) async {
    final url = '${ApiConstants.mainBaseUrl}/clientes/perfil/';
    final response = await _apiClient.patch(url, data, requiresAuth: true);

    if (response.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Error al actualizar perfil');
    }
  }
}
