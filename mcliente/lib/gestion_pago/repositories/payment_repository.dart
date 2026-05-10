import 'dart:convert';
import 'package:flutter/material.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';
import 'package:flutter_stripe/flutter_stripe.dart';

class PaymentRepository {
  final ApiClient _apiClient = ApiClient();
  final SecureStorageService _storage = SecureStorageService();

  Future<String> _getPagoUrl() async {
    final schemaName = await _storage.getSchemaName();
    if (schemaName == null || schemaName.isEmpty || schemaName == 'public') {
      return '${ApiConstants.mainBaseUrl}/pagos/';
    }
    return '${ApiConstants.tenantBaseUrl(schemaName)}/pagos/';
  }

  /// Crea un PaymentIntent en el backend y devuelve el client_secret
  Future<Map<String, dynamic>> createPaymentIntent(int pedidoId) async {
    final baseUrl = await _getPagoUrl();
    final url = '${baseUrl}create-payment-intent/';
    
    final response = await _apiClient.post(
      url,
      {'pedido_id': pedidoId},
      requiresAuth: true,
      includeTenantHost: true,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al crear PaymentIntent: ${response.body}');
    }
  }

  /// Procesa el pago usando el Payment Sheet de Stripe
  Future<bool> processPaymentSheet(int pedidoId) async {
    try {
      // 1. Obtener los datos del PaymentIntent desde el backend
      final paymentData = await createPaymentIntent(pedidoId);
      
      final String clientSecret = paymentData['paymentIntent'];
      final String? customerId = paymentData['customer'];
      final String? ephemeralKey = paymentData['ephemeralKey'];

      // 2. Inicializar el Payment Sheet
      await Stripe.instance.initPaymentSheet(
        paymentSheetParameters: SetupPaymentSheetParameters(
          paymentIntentClientSecret: clientSecret,
          customerId: customerId,
          customerEphemeralKeySecret: ephemeralKey,
          merchantDisplayName: 'MiQhatu Ecommerce',
          style: ThemeMode.light,
        ),
      );

      // 3. Mostrar el Payment Sheet
      await Stripe.instance.presentPaymentSheet();

      // 4. Confirmar el éxito al backend (opcional, el webhook también lo hará)
      await confirmPaymentSuccess(pedidoId);
      
      return true;
    } catch (e) {
      if (e is StripeException) {
        print('Error de Stripe: ${e.error.localizedMessage}');
      } else {
        print('Error procesando pago: $e');
      }
      return false;
    }
  }

  Future<void> confirmPaymentSuccess(int pedidoId) async {
    final baseUrl = await _getPagoUrl();
    final url = '${baseUrl}confirm-success/';
    final schemaName = await _storage.getSchemaName();
    
    await _apiClient.post(
      url,
      {
        'pedido_id': pedidoId,
        'tenant': schemaName,
      },
      requiresAuth: true,
      includeTenantHost: true,
    );
  }
}
