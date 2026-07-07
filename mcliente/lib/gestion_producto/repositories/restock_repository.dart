import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';

/// Repositorio de Solicitud de Restock / Intención de Compra (CU-25).
class RestockRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String> _baseUrl() async {
    final subdomain = await _storage.getSubdomain();
    if (subdomain == null || subdomain.isEmpty) {
      throw Exception('No hay tienda seleccionada.');
    }
    return ApiConstants.tenantBaseUrl(subdomain);
  }

  /// Registra el interés del cliente por un producto agotado.
  /// Devuelve el mensaje del backend para mostrar al usuario.
  Future<String> solicitar(int productoId) async {
    final base = await _baseUrl();
    final response = await _apiClient.post(
      '$base/restock/',
      {'producto_id': productoId},
      requiresAuth: true,
      includeTenantHost: true,
    );

    if (response.statusCode == 201 || response.statusCode == 200) {
      try {
        final d = jsonDecode(response.body);
        return d['mensaje'] ?? 'Te avisaremos cuando vuelva a haber stock.';
      } catch (_) {
        return 'Te avisaremos cuando vuelva a haber stock.';
      }
    }

    String msg = 'No se pudo registrar tu solicitud.';
    try {
      final d = jsonDecode(response.body);
      if (d is Map && d['error'] != null) msg = d['error'];
    } catch (_) {}
    throw Exception(msg);
  }
}
