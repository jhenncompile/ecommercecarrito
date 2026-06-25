import 'dart:convert';
import 'package:http/http.dart' as http;
import '../storage/secure_storage.dart';
import '../constants/api_constants.dart';
import '../../main.dart' as import_main;

/// Cliente HTTP centralizado con:
/// - Header `Authorization: Bearer <token>` automático
/// - Header `Host: subdomain.IP.nip.io` para django-tenants
/// - Interceptor de refresh automático cuando recibe 401
class ApiClient {
  final SecureStorageService _storage = SecureStorageService();

  // Flag para evitar bucles infinitos de refresh
  bool _isRefreshing = false;

  // ── HEADERS ──

  Future<Map<String, String>> _getHeaders({
    bool requiresAuth = false,
    bool includeTenantHost = false,
  }) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };

    // Bearer token para endpoints protegidos
    if (requiresAuth) {
      final token = await _storage.getAccessToken();
      if (token != null && token.isNotEmpty) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    // Host header para que django-tenants identifique el tenant
    if (includeTenantHost) {
      final subdomain = await _storage.getSubdomain();
      if (subdomain != null && subdomain.isNotEmpty) {
        headers['Host'] = ApiConstants.tenantHost(subdomain);
      }
    }

    return headers;
  }

  // ── MÉTODOS HTTP ──

  Future<http.Response> get(
    String url, {
    bool requiresAuth = false,
    bool includeTenantHost = false,
  }) async {
    final headers = await _getHeaders(
      requiresAuth: requiresAuth,
      includeTenantHost: includeTenantHost,
    );
    final response = await http.get(Uri.parse(url), headers: headers);

    // Si recibimos 401 y tenemos auth, intentar refresh
    if (response.statusCode == 401 && requiresAuth) {
      return await _handleTokenRefresh(() => get(
            url,
            requiresAuth: requiresAuth,
            includeTenantHost: includeTenantHost,
          ));
    }
    return response;
  }

  Future<http.Response> post(
    String url,
    Map<String, dynamic> body, {
    bool requiresAuth = false,
    bool includeTenantHost = false,
  }) async {
    final headers = await _getHeaders(
      requiresAuth: requiresAuth,
      includeTenantHost: includeTenantHost,
    );
    final response = await http.post(
      Uri.parse(url),
      headers: headers,
      body: jsonEncode(body),
    );

    if (response.statusCode == 401 && requiresAuth) {
      return await _handleTokenRefresh(() => post(
            url,
            body,
            requiresAuth: requiresAuth,
            includeTenantHost: includeTenantHost,
          ));
    }
    return response;
  }

  /// Método específico para subir archivos (audio) usando multipart/form-data
  Future<http.Response> multipartPost(
    String url, {
    required String filePath,
    required String fieldName,
    Map<String, String>? additionalFields,
    bool requiresAuth = false,
    bool includeTenantHost = false,
  }) async {
    final headers = await _getHeaders(
      requiresAuth: requiresAuth,
      includeTenantHost: includeTenantHost,
    );
    // Para multipart, no enviamos 'Content-Type': 'application/json'
    headers.remove('Content-Type');

    final request = http.MultipartRequest('POST', Uri.parse(url));
    request.headers.addAll(headers);

    if (additionalFields != null) {
      request.fields.addAll(additionalFields);
    }

    final file = await http.MultipartFile.fromPath(
      fieldName,
      filePath,
    );
    request.files.add(file);

    try {
      final streamedResponse = await request.send().timeout(
        const Duration(seconds: 120),
        onTimeout: () {
          throw Exception('Tiempo de espera agotado al subir el archivo (timeout).');
        },
      );
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 401 && requiresAuth) {
        return await _handleTokenRefresh(() => multipartPost(
              url,
              filePath: filePath,
              fieldName: fieldName,
              additionalFields: additionalFields,
              requiresAuth: requiresAuth,
              includeTenantHost: includeTenantHost,
            ));
      }
      return response;
    } catch (e) {
      if (e.toString().contains('SocketException') || e.toString().contains('Connection timed out')) {
        throw Exception('Error de red: No se pudo conectar al servidor ($url). Revisa tu IP y conexión.');
      }
      rethrow;
    }
  }

  Future<http.Response> put(
    String url,
    Map<String, dynamic> body, {
    bool requiresAuth = false,
    bool includeTenantHost = false,
  }) async {
    final headers = await _getHeaders(
      requiresAuth: requiresAuth,
      includeTenantHost: includeTenantHost,
    );
    final response = await http.put(
      Uri.parse(url),
      headers: headers,
      body: jsonEncode(body),
    );

    if (response.statusCode == 401 && requiresAuth) {
      return await _handleTokenRefresh(() => put(
            url,
            body,
            requiresAuth: requiresAuth,
            includeTenantHost: includeTenantHost,
          ));
    }
    return response;
  }

  Future<http.Response> patch(
    String url,
    Map<String, dynamic> body, {
    bool requiresAuth = false,
    bool includeTenantHost = false,
  }) async {
    final headers = await _getHeaders(
      requiresAuth: requiresAuth,
      includeTenantHost: includeTenantHost,
    );
    final response = await http.patch(
      Uri.parse(url),
      headers: headers,
      body: jsonEncode(body),
    );

    if (response.statusCode == 401 && requiresAuth) {
      return await _handleTokenRefresh(() => patch(
            url,
            body,
            requiresAuth: requiresAuth,
            includeTenantHost: includeTenantHost,
          ));
    }
    return response;
  }

  Future<http.Response> delete(
    String url, {
    bool requiresAuth = false,
    bool includeTenantHost = false,
  }) async {
    final headers = await _getHeaders(
      requiresAuth: requiresAuth,
      includeTenantHost: includeTenantHost,
    );
    final response = await http.delete(Uri.parse(url), headers: headers);

    if (response.statusCode == 401 && requiresAuth) {
      return await _handleTokenRefresh(() => delete(
            url,
            requiresAuth: requiresAuth,
            includeTenantHost: includeTenantHost,
          ));
    }
    return response;
  }

  // ── INTERCEPTOR DE REFRESH AUTOMÁTICO ──
  //
  // Flujo: petición original → 401 → refresh → reintento → éxito/fallo
  //
  // Si el refresh también falla, borra tokens y devuelve el 401 original
  // para que la capa superior (repository/screen) maneje el redirect a login.

  Future<http.Response> _handleTokenRefresh(
    Future<http.Response> Function() retryRequest,
  ) async {
    // Evitar bucle infinito si el refresh ya está en progreso
    if (_isRefreshing) {
      return http.Response('{"detail": "Token refresh en progreso"}', 401);
    }

    _isRefreshing = true;

    try {
      final refreshToken = await _storage.getRefreshToken();

      if (refreshToken == null || refreshToken.isEmpty) {
        await _storage.deleteAll();
        _isRefreshing = false;
        return http.Response('{"detail": "No hay refresh token"}', 401);
      }

      // Llamar al endpoint de refresh (sin auth, sin tenant host)
      final refreshResponse = await http.post(
        Uri.parse('${ApiConstants.mainBaseUrl}${ApiConstants.refresh}'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refreshToken}),
      );

      if (refreshResponse.statusCode == 200) {
        final data = jsonDecode(refreshResponse.body);
        final newAccessToken = data['access'] as String;

        // Guardar el nuevo token
        await _storage.saveAccessToken(newAccessToken);

        _isRefreshing = false;

        // Reintentar la petición original con el nuevo token
        return await retryRequest();
      } else {
        // El refresh token también expiró → limpiar todo
        await _storage.deleteAll();
        _isRefreshing = false;
        _forceLogout();
        return refreshResponse;
      }
    } catch (e) {
      await _storage.deleteAll();
      _isRefreshing = false;
      _forceLogout();
      return http.Response('{"detail": "Error en refresh: $e"}', 401);
    }
  }

  void _forceLogout() {
    import_main.navigatorKey.currentState?.pushNamedAndRemoveUntil('/login', (route) => false);
  }
}