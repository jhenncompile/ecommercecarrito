import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../models/cliente_model.dart';

class ClienteRepository {
  final ApiClient _apiClient = ApiClient();

  Future<List<ClientModel>> getClientes() async {
    final url = '${ApiConstants.mainBaseUrl}/clientes/';
    try {
      final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);
      if (response.statusCode == 200) {
        final dynamic decoded = jsonDecode(response.body);
        final List<dynamic> data = (decoded is Map && decoded.containsKey('results')) 
            ? decoded['results'] 
            : decoded;
        return data.map((json) => ClientModel.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  Future<bool> registerCliente(Map<String, dynamic> data) async {
    final url = '${ApiConstants.mainBaseUrl}/clientes/';
    try {
      // Para el registro de cliente desde el vendedor, no queremos autologin, 
      // solo crear el registro. El backend /clientes/ POST hace ambas cosas, 
      // pero el vendedor simplemente ignora los tokens devueltos.
      final response = await _apiClient.post(url, data, requiresAuth: true, includeTenantHost: true);
      return response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  Future<List<ClientModel>> searchClientes(String query) async {
    final url = '${ApiConstants.mainBaseUrl}/clientes/?search=$query';
    try {
      final response = await _apiClient.get(url, requiresAuth: true, includeTenantHost: true);
      if (response.statusCode == 200) {
        final dynamic decoded = jsonDecode(response.body);
        final List<dynamic> data = (decoded is Map && decoded.containsKey('results')) 
            ? decoded['results'] 
            : decoded;
        return data.map((json) => ClientModel.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }
}
