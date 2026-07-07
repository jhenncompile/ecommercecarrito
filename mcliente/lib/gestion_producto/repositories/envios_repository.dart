import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';

/// Repositorio de Logística y Envíos (CU-24). Expone la configuración que el
/// storefront necesita (por ahora, el WhatsApp de la tienda para el checkout).
class EnviosRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String> _baseUrl() async {
    final subdomain = await _storage.getSubdomain();
    if (subdomain == null || subdomain.isEmpty) {
      throw Exception('No hay tienda seleccionada.');
    }
    return ApiConstants.tenantBaseUrl(subdomain);
  }

  /// Devuelve el número de WhatsApp de la tienda (o null si no está configurado).
  Future<String?> obtenerWhatsapp() async {
    final base = await _baseUrl();
    final response = await _apiClient.get(
      '$base/envios/config/',
      requiresAuth: false,
      includeTenantHost: true,
    );
    if (response.statusCode == 200) {
      try {
        final d = jsonDecode(response.body);
        final w = d['whatsapp'];
        return (w == null || w.toString().isEmpty) ? null : w.toString();
      } catch (_) {
        return null;
      }
    }
    return null;
  }
}
