// =========================================================================
// API CONSTANTS - Configuración Centralizada (mcliente - consumidor)
// =========================================================================
// La IP y puerto se inyectan en tiempo de compilación via --dart-define:
//   flutter run --dart-define=API_IP=157.173.102.129 --dart-define=API_PORT=8001
//
// Si no se pasa nada, usa valores de desarrollo (localhost).
// =========================================================================

class ApiConstants {
  // ── IP y Puerto (inyectados via --dart-define o valor por defecto) ──
  static const String vpsIp = String.fromEnvironment(
    'API_IP',
    defaultValue: '192.168.100.244', // ← Cambiar solo aquí en desarrollo
  );

  static const String djangoPort = String.fromEnvironment(
    'API_PORT',
    defaultValue: '8001',
  );

  // ── URL BASE principal (autenticación, no-tenant) ──
  static const String mainBaseUrl = 'http://$vpsIp:$djangoPort/api';

  // ── URL para peticiones dentro de un tenant ──
  // Formato: http://mitienda.157.173.102.129.nip.io:8001/api
  static String tenantBaseUrl(String schemaName) {
    final slug = schemaName.replaceAll('_', '');
    return 'http://$slug.$vpsIp.nip.io:$djangoPort/api';
  }

  // ── Header Host para django-tenants ──
  static String tenantHost(String schemaName) {
    final slug = schemaName.replaceAll('_', '');
    return '$slug.$vpsIp.nip.io';
  }

  // ── Auth Endpoints (IP directa, sin tenant) ──
  static const String login = '/token/';
  static const String refresh = '/token/refresh/';
  static const String logout = '/logout/';

  // ── Tenant Endpoints ──
  static const String productos = '/productos/';
  static const String categorias = '/categorias/';
  static const String pedidos = '/pedidos/';
}
