import 'dart:convert';
import 'package:http/http.dart' as http;
import '../storage/secure_storage.dart';
import '../constants/api_constants.dart';

class ApiClient {
  final SecureStorageService _storage = SecureStorageService();
  bool _isRefreshing = false;

  Future<Map<String, String>> _getHeaders({
    bool requiresAuth = false,
    bool includeTenantHost = false,
  }) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };

    if (requiresAuth) {
      final token = await _storage.getAccessToken();
      if (token != null && token.isNotEmpty) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    if (includeTenantHost) {
      final subdomain = await _storage.getSubdomain();
      if (subdomain != null && subdomain.isNotEmpty) {
        headers['Host'] = ApiConstants.tenantHost(subdomain);
      }
    }

    return headers;
  }

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

  Future<http.Response> _handleTokenRefresh(
    Future<http.Response> Function() retryRequest,
  ) async {
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

      final refreshResponse = await http.post(
        Uri.parse('${ApiConstants.mainBaseUrl}${ApiConstants.refresh}'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refreshToken}),
      );

      if (refreshResponse.statusCode == 200) {
        final data = jsonDecode(refreshResponse.body);
        final newAccessToken = data['access'] as String;

        await _storage.saveAccessToken(newAccessToken);
        _isRefreshing = false;
        return await retryRequest();
      } else {
        await _storage.deleteAll();
        _isRefreshing = false;
        return refreshResponse;
      }
    } catch (e) {
      await _storage.deleteAll();
      _isRefreshing = false;
      return http.Response('{"detail": "Error en refresh: $e"}', 401);
    }
  }
}
