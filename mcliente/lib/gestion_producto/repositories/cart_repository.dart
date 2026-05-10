import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';
import '../models/cart_model.dart';

class CartRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String> _getCartUrl() async {
    final schemaName = await _storage.getSchemaName();
    if (schemaName == null || schemaName.isEmpty || schemaName == 'public') {
      return '${ApiConstants.mainBaseUrl}/carritos/';
    }
    return '${ApiConstants.tenantBaseUrl(schemaName)}/carritos/';
  }

  Future<CartModel> fetchActiveCart() async {
    final url = await _getCartUrl();
    // El backend maneja obtener o crear el carrito abierto cuando se llama a POST carritos/
    final response = await _apiClient.post(url, {}, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200 || response.statusCode == 201) {
      return CartModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Error al obtener el carrito: ${response.body}');
    }
  }

  Future<CartModel> addItem(int cartId, int productId, {int quantity = 1}) async {
    final baseUrl = await _getCartUrl();
    final url = '$baseUrl$cartId/agregar-item/';
    
    final response = await _apiClient.post(
      url, 
      {'producto_id': productId, 'cantidad': quantity}, 
      requiresAuth: true, 
      includeTenantHost: true
    );

    if (response.statusCode == 200) {
      return CartModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Error al agregar item: ${response.body}');
    }
  }

  Future<CartModel> removeItem(int cartId, int productId) async {
    final baseUrl = await _getCartUrl();
    final url = '$baseUrl$cartId/eliminar-item/';
    
    final response = await _apiClient.post(
      url, 
      {'producto_id': productId}, 
      requiresAuth: true, 
      includeTenantHost: true
    );

    if (response.statusCode == 200) {
      return CartModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Error al eliminar item: ${response.body}');
    }
  }

  Future<CartModel> clearCart(int cartId) async {
    final baseUrl = await _getCartUrl();
    final url = '$baseUrl$cartId/vaciar/';
    
    final response = await _apiClient.post(url, {}, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      return CartModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Error al vaciar carrito');
    }
  }

  Future<CartModel> checkout(int cartId) async {
    final baseUrl = await _getCartUrl();
    final url = '$baseUrl$cartId/cerrar/';
    
    final response = await _apiClient.post(url, {}, requiresAuth: true, includeTenantHost: true);

    if (response.statusCode == 200) {
      return CartModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Error al procesar pedido');
    }
  }
}
