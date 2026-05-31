// =========================================================================
// API CONSTANTS - Configuración Centralizada (movil - vendedor)
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
  // El subdomain viene del backend (ej: tienda1.192.168.x.x.nip.io o tienda1.miqhatu.com)
  static String tenantBaseUrl(String subdomain) {
    return 'http://$vpsIp:$djangoPort/api';
  }

  // ── Header Host para django-tenants ──
  static String tenantHost(String subdomain) {
    return subdomain;
  }

  // ── Auth Endpoints (IP directa, sin tenant) ──
  static const String login = '/token/';
  static const String refresh = '/token/refresh/';
  static const String logout = '/logout/';

  // ── Tenant Endpoints ──
  static const String dashboard = '/dashboard/';
  static const String productos = '/productos/';
  static const String vquery = '/vquery/';
}