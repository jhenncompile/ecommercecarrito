import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';
import '../models/order_model.dart';

class OrderRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String> _getOrdersUrl() async {
    final schemaName = await _storage.getSchemaName();
    if (schemaName == null || schemaName.isEmpty || schemaName == 'public') {
      return '${ApiConstants.mainBaseUrl}/pedidos/';
    }
    return '${ApiConstants.tenantBaseUrl(schemaName)}/pedidos/';
  }

  Future<List<OrderModel>> fetchMyOrders() async {
    final url = await _getOrdersUrl();
    final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => OrderModel.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar pedidos');
    }
  }

  /// Obtiene pedidos de todos los tenants para el usuario autenticado
  Future<List<OrderModel>> fetchGlobalOrders() async {
    final url = await _getOrdersUrl();
    final globalUrl = '${url}global-list/';
    
    final response = await _apiClient.get(globalUrl, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => OrderModel.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar historial global');
    }
  }
}
