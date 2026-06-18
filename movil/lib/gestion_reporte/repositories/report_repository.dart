import 'dart:convert';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';

class ReportRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String?> _buildUrl() async {
    final subdomain = await _storage.getSubdomain();
    if (subdomain == null || subdomain.isEmpty) return null;
    return ApiConstants.tenantBaseUrl(subdomain);
  }

  Future<Map<String, dynamic>> sendVoiceQuery(String filePath) async {
    final baseUrl = await _buildUrl();
    if (baseUrl == null) throw Exception('No hay tenant configurado.');
    final url = '$baseUrl${ApiConstants.vquery}';
    
    final response = await _apiClient.multipartPost(
      url,
      filePath: filePath,
      fieldName: 'audio',
      requiresAuth: true,
      includeTenantHost: true,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 202) {
      final data = jsonDecode(response.body);
      final taskId = data['task_id'];
      if (taskId != null) {
        return await _pollTaskStatus(baseUrl, taskId);
      }
      throw Exception('Error al procesar la consulta (sin task_id).');
    } else {
      final errorData = jsonDecode(response.body);
      throw Exception(errorData['error'] ?? 'Error al procesar la consulta.');
    }
  }

  Future<Map<String, dynamic>> _pollTaskStatus(String baseUrl, String taskId) async {
    final url = '$baseUrl/vquery/status/$taskId/';
    while (true) {
      await Future.delayed(const Duration(seconds: 2));
      final response = await _apiClient.get(
        url,
        requiresAuth: true,
        includeTenantHost: true,
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['status'] == 'SUCCESS') {
          return data;
        } else if (data['status'] == 'FAILURE') {
          throw Exception(data['error'] ?? 'La consulta por voz falló.');
        }
        // Si es PENDING o PROCESSING, continúa el bucle
      } else {
        throw Exception('Error al consultar el estado de la tarea.');
      }
    }
  }

  // --- REPORTES ESTÁTICOS ---
  Future<List<dynamic>> getReporteEstatico(String tipo) async {
    final baseUrl = await _buildUrl();
    if (baseUrl == null) return [];
    final url = '$baseUrl/reportes/estatico/$tipo/';
    
    try {
      final response = await _apiClient.get(
        url,
        requiresAuth: true,
        includeTenantHost: true,
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // --- REPORTES DINÁMICOS ---
  Future<List<dynamic>> getReportesDinamicosGuardados() async {
    final baseUrl = await _buildUrl();
    if (baseUrl == null) return [];
    final url = '$baseUrl/reportes/configuraciones/';
    
    try {
      final response = await _apiClient.get(
        url,
        requiresAuth: true,
        includeTenantHost: true,
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  Future<List<dynamic>> ejecutarReporteDinamico(Map<String, dynamic> config) async {
    final baseUrl = await _buildUrl();
    if (baseUrl == null) throw Exception('No hay tenant configurado.');
    final url = '$baseUrl/reportes/builder/';
    
    final response = await _apiClient.post(
      url,
      config,
      requiresAuth: true,
      includeTenantHost: true,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      final errorData = jsonDecode(response.body);
      throw Exception(errorData['error'] ?? 'Error al ejecutar reporte.');
    }
  }

  // --- PREDICCIONES ---
  Future<Map<String, dynamic>> getPrediccion(String tipoEndpoint, Map<String, dynamic> params) async {
    final baseUrl = await _buildUrl();
    if (baseUrl == null) throw Exception('No hay tenant configurado.');
    
    // Todos los forecasts van por POST a /reportes/prediccion/ según la web
    final uri = Uri.parse('$baseUrl/reportes/prediccion/');
    
    final response = await _apiClient.post(
      uri.toString(),
      params,
      requiresAuth: true,
      includeTenantHost: true,
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      try {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['error'] ?? 'Error al generar predicción.');
      } catch (_) {
        throw Exception('Error al generar predicción (status ${response.statusCode}).');
      }
    }
  }

  Future<List<dynamic>> getPrediccionOpciones(String endpoint) async {
    final baseUrl = await _buildUrl();
    if (baseUrl == null) return [];
    final uri = Uri.parse('$baseUrl/reportes/prediccion/$endpoint/');
    final response = await _apiClient.get(
      uri.toString(),
      requiresAuth: true,
      includeTenantHost: true,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  }
}
