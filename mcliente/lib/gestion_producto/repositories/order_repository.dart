import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';
import '../models/order_model.dart';

class OrderRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String?> _buildUrl() async {
    final subdomain = await _storage.getSubdomain();
    if (subdomain == null || subdomain.isEmpty) return null;
    return '${ApiConstants.tenantBaseUrl(subdomain)}/pedidos/';
  }

  Future<List<OrderModel>> fetchOrders() async {
    final url = await _buildUrl();
    if (url == null) throw Exception('No hay tenant configurado.');
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      final dynamic decoded = jsonDecode(response.body);
      final List<dynamic> data = (decoded is Map) ? (decoded['results'] ?? []) : decoded;
      return data.map((json) => OrderModel.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar pedidos');
    }
  }

  /// Obtiene pedidos de todos los tenants para el usuario autenticado
  Future<List<OrderModel>> fetchGlobalOrders() async {
    final globalUrl = '${ApiConstants.mainBaseUrl}/pedidos/global-list/';
    
    final response = await _apiClient.get(globalUrl, requiresAuth: true, includeTenantHost: false);

    if (response.statusCode == 200) {
      final dynamic decoded = jsonDecode(response.body);
      final List<dynamic> data = (decoded is Map) ? (decoded['results'] ?? []) : decoded;
      return data.map((json) => OrderModel.fromJson(json)).toList();
    } else {
      return [];
    }
  }

  Future<OrderModel> getOrderDetail(int orderId) async {
    final baseUrl = await _buildUrl();
    if (baseUrl == null) throw Exception('No hay tenant configurado.');
    final url = '$baseUrl$orderId/';
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      return OrderModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Error al cargar detalle del pedido');
    }
  }
}
