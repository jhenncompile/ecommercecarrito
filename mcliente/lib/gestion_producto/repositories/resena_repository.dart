import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';
import '../models/resena_model.dart';

/// Repositorio de Reseñas y Calificaciones (CU-27).
class ResenaRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String> _baseUrl() async {
    final subdomain = await _storage.getSubdomain();
    if (subdomain == null || subdomain.isEmpty) {
      throw Exception('No hay tienda seleccionada.');
    }
    return ApiConstants.tenantBaseUrl(subdomain);
  }

  /// Obtiene el resumen + lista de reseñas de un producto (y la reseña propia).
  Future<ResenasData> fetchResenas(int productId) async {
    final base = await _baseUrl();
    final url = '$base/resenas/producto/$productId/';
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      return ResenasData.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    }
    return ResenasData.empty();
  }

  /// Crea o actualiza la reseña del cliente autenticado.
  Future<void> enviarResena(int productId, int calificacion, String comentario) async {
    final base = await _baseUrl();
    final url = '$base/resenas/';
    final response = await _apiClient.post(
      url,
      {'producto_id': productId, 'calificacion': calificacion, 'comentario': comentario},
      requiresAuth: true,
      includeTenantHost: true,
    );

    if (response.statusCode != 201 && response.statusCode != 200) {
      String msg = 'No se pudo enviar la reseña.';
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is Map && decoded['error'] != null) msg = decoded['error'];
      } catch (_) {}
      throw Exception(msg);
    }
  }
}
