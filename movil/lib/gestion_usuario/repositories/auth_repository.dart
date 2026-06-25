import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';
import '../../core/services/push_notification_service.dart';
import '../models/auth_tokens.dart';
import '../../main.dart' as import_main;

class AuthRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  // ── ENDPOINT 1: LOGIN ──
  // POST /api/token/ → {access, refresh, schema_name, subdomain}
  Future<bool> login(String username, String password) async {
    final url = '${ApiConstants.mainBaseUrl}${ApiConstants.login}';
    print('🔵 LOGIN: Enviando a → $url');
    print('🔵 LOGIN: username=$username');

    try {
      final response = await _apiClient.post(
        url,
        {'username': username, 'password': password},
      );

      print('🔵 LOGIN: Status → ${response.statusCode}');
      print('🔵 LOGIN: Body → ${response.body}');

      if (response.statusCode == 200) {
        final tokens = AuthTokens.fromJson(jsonDecode(response.body));

        // Guardar tokens JWT
        await _storage.saveTokens(tokens.access, tokens.refresh);

        // Guardar info del tenant para las peticiones futuras
        await _storage.saveTenantInfo(tokens.schemaName, tokens.subdomain);

        print('🟢 LOGIN: Éxito. Tenant=${tokens.subdomain}, Schema=${tokens.schemaName}');
        
        final token = await PushNotificationService.getToken();
        if (token != null) {
          await PushNotificationService.registerTokenWithBackend(token);
        }
        
        return true;
      }
      print('🔴 LOGIN: Falló con status ${response.statusCode}');
      return false;
    } catch (e) {
      print('🔴 LOGIN: Excepción → $e');
      return false;
    }
  }

  // ── ENDPOINT 2: REFRESCAR TOKEN ──
  Future<bool> refreshToken() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await _apiClient.post(
        '${ApiConstants.mainBaseUrl}${ApiConstants.refresh}',
        {'refresh': refreshToken},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await _storage.saveAccessToken(data['access']);
        return true;
      } else {
        await _storage.deleteAll();
        return false;
      }
    } catch (e) {
      return false;
    }
  }

  // ── ENDPOINT 3: LOGOUT ──
  Future<void> logout() async {
    try {
      final refreshToken = await _storage.getRefreshToken();

      if (refreshToken != null) {
        await _apiClient.post(
          '${ApiConstants.mainBaseUrl}${ApiConstants.logout}',
          {'refresh': refreshToken},
        );
      }
    } catch (_) {
      // Si falla la petición al servidor, igual borramos localmente
    } finally {
      await _storage.deleteAll();
      import_main.navigatorKey.currentState?.pushNamedAndRemoveUntil('/login', (route) => false);
    }
  }

  // ── ENDPOINT 4: RECUPERAR CONTRASEÑA ──
  Future<Map<String, dynamic>> resetPassword(String email) async {
    final url = '${ApiConstants.mainBaseUrl}/password-reset/';
    try {
      final response = await _apiClient.post(url, {'email': email});
      
      final data = jsonDecode(response.body);
      if (response.statusCode == 200 || response.statusCode == 201) {
        return {
          'success': true,
          'message': data['message'] ?? 'Si el email existe, recibirás un enlace.',
          'dev_reset_url': data['dev_reset_url']
        };
      }
      return {
        'success': false,
        'error': data['error'] ?? 'Error al procesar la solicitud.',
      };
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  // ── ENDPOINT 5: CREAR TIENDA (Gratuita) ──
  Future<Map<String, dynamic>> createStore(Map<String, dynamic> data) async {
    final url = '${ApiConstants.mainBaseUrl}/tiendas/crear/';
    try {
      final response = await _apiClient.post(url, data);
      final body = jsonDecode(response.body);
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        return {
          'success': true,
          'data': body
        };
      }
      return {
        'success': false,
        'error': body['error'] ?? 'Error al crear la tienda',
      };
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  // ── ENDPOINT 6: OBTENER PLANES ──
  Future<List<Map<String, dynamic>>> fetchPlanes() async {
    final url = '${ApiConstants.mainBaseUrl}/planes/';
    try {
      final response = await _apiClient.get(url);
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.cast<Map<String, dynamic>>();
      }
      return [];
    } catch (e) {
      print('🔴 Error fetchPlanes: $e');
      return [];
    }
  }

  // ── ENDPOINT 7: CHECKOUT SUSCRIPCIÓN (Stripe Intent) ──
  Future<Map<String, dynamic>> checkoutSuscripcion(Map<String, dynamic> data) async {
    final url = '${ApiConstants.mainBaseUrl}/tiendas/checkout-suscripcion/';
    try {
      final response = await _apiClient.post(url, data);
      final body = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return {
          'success': true,
          'data': body
        };
      }
      return {
        'success': false,
        'error': body['error'] ?? 'Error al inicializar el pago',
      };
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  // ── ENDPOINT 8: CREAR TIENDA CON PAGO ──
  Future<Map<String, dynamic>> createStoreWithPayment(Map<String, dynamic> data) async {
    final url = '${ApiConstants.mainBaseUrl}/tiendas/crear-con-pago/';
    try {
      final response = await _apiClient.post(url, data);
      final body = jsonDecode(response.body);
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        return {
          'success': true,
          'data': body
        };
      }
      return {
        'success': false,
        'error': body['error'] ?? 'Error al crear la tienda con pago',
      };
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  // ── UTILIDADES ──
  Future<bool> isLoggedIn() async {
    final token = await _storage.getAccessToken();
    return token != null && token.isNotEmpty;
  }

  Future<String?> getAccessToken() async {
    return await _storage.getAccessToken();
  }

  Future<String?> getSubdomain() async {
    return await _storage.getSubdomain();
  }

  Future<String?> getSchemaName() async {
    return await _storage.getSchemaName();
  }
}