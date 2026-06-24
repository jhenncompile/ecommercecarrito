import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';
import '../models/product_model.dart';


class ProductRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String?> _buildUrl() async {
    final subdomain = await _storage.getSubdomain();
    if (subdomain == null || subdomain.isEmpty) return null;
    return '${ApiConstants.tenantBaseUrl(subdomain)}${ApiConstants.productos}';
  }

  Future<String?> _buildCategoriesUrl() async {
    final subdomain = await _storage.getSubdomain();
    if (subdomain == null || subdomain.isEmpty) return null;
    return '${ApiConstants.tenantBaseUrl(subdomain)}${ApiConstants.categorias}';
  }

  Future<List<ProductModel>> fetchProducts({int? categoryId}) async {
    final baseUrl = await _buildUrl();
    if (baseUrl == null) throw Exception('No hay tenant configurado.');
    final url = categoryId != null ? '$baseUrl?categoria=$categoryId' : baseUrl;
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      final dynamic decoded = jsonDecode(response.body);
      final List<dynamic> data = (decoded is Map) ? (decoded['results'] ?? []) : decoded;
      return data.map((json) => ProductModel.fromJson(json)).toList();
    } else {
      String errMsg = 'Error al cargar productos: ${response.statusCode}';
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is Map && decoded.containsKey('detail')) errMsg = decoded['detail'];
        else if (decoded is Map && decoded.containsKey('error')) errMsg = decoded['error'];
        else if (decoded is Map) errMsg = decoded.toString();
      } catch (_) {}
      throw Exception(errMsg);
    }
  }

  Future<List<Map<String, dynamic>>> fetchCategories() async {
    final url = await _buildCategoriesUrl();
    if (url == null) throw Exception('No hay tenant configurado.');
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      final dynamic decoded = jsonDecode(response.body);
      final List<dynamic> data = (decoded is Map) ? (decoded['results'] ?? []) : decoded;
      return data.cast<Map<String, dynamic>>();
    } else {
      return [];
    }
  }

  Future<List<ProductModel>> fetchRecommendations(int productId) async {
    final subdomain = await _storage.getSubdomain();
    if (subdomain == null || subdomain.isEmpty) throw Exception('No hay tenant configurado.');
    final url = '${ApiConstants.tenantBaseUrl(subdomain)}/catalogo/$productId/recomendaciones/';
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = jsonDecode(response.body);
      final List<dynamic> recs = data['recommendations'] ?? [];
      return recs.map((json) => ProductModel.fromJson(json)).toList();
    } else {
      String errMsg = 'Error al cargar recomendaciones: ${response.statusCode}';
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is Map && decoded.containsKey('detail')) errMsg = decoded['detail'];
        else if (decoded is Map && decoded.containsKey('error')) errMsg = decoded['error'];
        else if (decoded is Map) errMsg = decoded.toString();
      } catch (_) {}
      throw Exception(errMsg);
    }
  }
}
