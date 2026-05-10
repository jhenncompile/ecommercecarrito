import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';
import '../models/product_model.dart';

class ProductRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String> _getProductsUrl() async {
    final schemaName = await _storage.getSchemaName();
    if (schemaName == null || schemaName.isEmpty || schemaName == 'public') {
      return '${ApiConstants.mainBaseUrl}${ApiConstants.productos}';
    }
    return '${ApiConstants.tenantBaseUrl(schemaName)}${ApiConstants.productos}';
  }

  Future<List<ProductModel>> fetchProducts({int? categoryId}) async {
    final baseUrl = await _getProductsUrl();
    final url = categoryId != null ? '$baseUrl?categoria=$categoryId' : baseUrl;
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => ProductModel.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar productos');
    }
  }

  Future<List<Map<String, dynamic>>> fetchCategories() async {
    final schemaName = await _storage.getSchemaName();
    if (schemaName == null) return [];
    
    final url = '${ApiConstants.tenantBaseUrl(schemaName)}${ApiConstants.categorias}';
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.cast<Map<String, dynamic>>();
    } else {
      return [];
    }
  }

  Future<List<ProductModel>> fetchRecommendations(int productId) async {
    final baseUrl = await _getProductsUrl();
    final url = '$baseUrl$productId/recomendaciones/';
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = jsonDecode(response.body);
      final List<dynamic> recs = data['recommendations'] ?? [];
      return recs.map((json) => ProductModel.fromJson(json)).toList();
    } else {
      return [];
    }
  }
}
