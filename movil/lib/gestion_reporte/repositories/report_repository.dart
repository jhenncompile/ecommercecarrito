import 'dart:convert';
import 'package:flutter_stripe/flutter_stripe.dart';
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
    } else if (response.statusCode == 403) {
      throw Exception('PLAN_REQUIRED');
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
      } else if (response.statusCode == 403) {
        throw Exception('PLAN_REQUIRED');
      }
      return [];
    } catch (e) {
      if (e.toString().contains('PLAN_REQUIRED')) rethrow;
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
      } else if (response.statusCode == 403) {
        throw Exception('PLAN_REQUIRED');
      }
      return [];
    } catch (e) {
      if (e.toString().contains('PLAN_REQUIRED')) rethrow;
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
    } else if (response.statusCode == 403) {
      throw Exception('PLAN_REQUIRED');
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
    } else if (response.statusCode == 403) {
      throw Exception('PLAN_REQUIRED');
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
    } else if (response.statusCode == 403) {
      throw Exception('PLAN_REQUIRED');
    }
    return [];
  }

  // --- UPGRADE PLAN ---
  Future<void> upgradePlan() async {
    final subdomain = await _storage.getSubdomain();
    if (subdomain == null || subdomain.isEmpty) throw Exception('No hay tenant configurado.');
    
    final url = '${ApiConstants.mainBaseUrl}/tienda/suscripcion/upgrade/';
    
    // 1. Obtener clientSecret y publishableKey
    final response = await _apiClient.post(
      url,
      {'plan_id': 2}, // Profesional
      requiresAuth: true,
      includeTenantHost: true,
    );
    
    if (response.statusCode != 200) {
      throw Exception('Error al iniciar pago: ${response.body}');
    }

    final data = jsonDecode(response.body);
    final clientSecret = data['clientSecret'];
    final publishableKey = data['publishableKey'];

    if (clientSecret == null || publishableKey == null) {
      throw Exception('No se recibió la configuración de pago de Stripe.');
    }

    // 2. Configurar Stripe
    Stripe.publishableKey = publishableKey;

    // 3. Inicializar Payment Sheet
    await Stripe.instance.initPaymentSheet(
      paymentSheetParameters: SetupPaymentSheetParameters(
        paymentIntentClientSecret: clientSecret,
        merchantDisplayName: 'MiQhatu Premium',
      ),
    );

    // 4. Mostrar Payment Sheet
    try {
      await Stripe.instance.presentPaymentSheet();
    } catch (e) {
      if (e is StripeException) {
        throw Exception('Pago cancelado o fallido: ${e.error.localizedMessage}');
      } else {
        throw Exception('Error en el pago: $e');
      }
    }

    // 5. Confirmar pago en backend
    final paymentIntentId = clientSecret.split('_secret')[0];
    final confirmResponse = await _apiClient.post(
      url,
      {
        'plan_id': 2,
        'payment_intent': paymentIntentId
      },
      requiresAuth: true,
      includeTenantHost: true,
    );

    if (confirmResponse.statusCode != 200) {
      throw Exception('Error al confirmar mejora: ${confirmResponse.body}');
    }
  }
}
