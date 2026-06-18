// movil/lib/gestion_recordatorio/repositories/recordatorio_repository.dart
import 'dart:convert';
import '../../core/network/api_client.dart';
import '../models/recordatorio_model.dart';

class RecordatorioRepository {
  final ApiClient _api = ApiClient();

  // ── Listar todos los recordatorios (con filtros opcionales) ──
  Future<List<RecordatorioModel>> getRecordatorios({
    String? tipo,
    bool? completado,
  }) async {
    String url = '/recordatorios/';
    final params = <String>[];
    if (tipo != null && tipo.isNotEmpty) params.add('tipo=$tipo');
    if (completado != null) params.add('completado=$completado');
    if (params.isNotEmpty) url += '?${params.join('&')}';

    final response = await _api.get(
      url,
      requiresAuth: true,
      includeTenantHost: true,
    );

    if (response.statusCode == 200) {
      final decoded = json.decode(utf8.decode(response.bodyBytes));
      final List<dynamic> items =
          decoded is Map ? (decoded['results'] ?? []) : decoded;
      return items
          .map((e) => RecordatorioModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Error al obtener recordatorios (${response.statusCode})');
  }

  // ── Próximos 7 días ──────────────────────────────────────────
  Future<List<RecordatorioModel>> getProximos() async {
    final response = await _api.get(
      '/recordatorios/proximos/',
      requiresAuth: true,
      includeTenantHost: true,
    );
    if (response.statusCode == 200) {
      final decoded = json.decode(utf8.decode(response.bodyBytes));
      final List<dynamic> items =
          decoded is Map ? (decoded['results'] ?? []) : decoded;
      return items
          .map((e) => RecordatorioModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  // ── Crear ───────────────────────────────────────────────────
  Future<RecordatorioModel> crearRecordatorio(Map<String, dynamic> body) async {
    final response = await _api.post(
      '/recordatorios/',
      body,
      requiresAuth: true,
      includeTenantHost: true,
    );
    if (response.statusCode == 201) {
      final decoded = json.decode(utf8.decode(response.bodyBytes));
      return RecordatorioModel.fromJson(decoded as Map<String, dynamic>);
    }
    final err = _parseError(response.body);
    throw Exception('Error al crear recordatorio: $err');
  }

  // ── Actualizar ──────────────────────────────────────────────
  Future<RecordatorioModel> actualizarRecordatorio(
    int id,
    Map<String, dynamic> body,
  ) async {
    final response = await _api.patch(
      '/recordatorios/$id/',
      body,
      requiresAuth: true,
      includeTenantHost: true,
    );
    if (response.statusCode == 200) {
      final decoded = json.decode(utf8.decode(response.bodyBytes));
      return RecordatorioModel.fromJson(decoded as Map<String, dynamic>);
    }
    throw Exception('Error al actualizar recordatorio');
  }

  // ── Eliminar ────────────────────────────────────────────────
  Future<void> eliminarRecordatorio(int id) async {
    final response = await _api.delete(
      '/recordatorios/$id/',
      requiresAuth: true,
      includeTenantHost: true,
    );
    if (response.statusCode != 204) {
      throw Exception('Error al eliminar recordatorio');
    }
  }

  // ── Marcar completado (CU-18 notificación) ──────────────────
  Future<RecordatorioModel> marcarCompletado(int id) async {
    final response = await _api.post(
      '/recordatorios/$id/marcar-completado/',
      {},
      requiresAuth: true,
      includeTenantHost: true,
    );
    if (response.statusCode == 200) {
      final decoded = json.decode(utf8.decode(response.bodyBytes));
      return RecordatorioModel.fromJson(decoded as Map<String, dynamic>);
    }
    throw Exception('Error al marcar como completado');
  }

  // ── Helper para parsear errores ─────────────────────────────
  String _parseError(String body) {
    try {
      final decoded = json.decode(body);
      if (decoded is Map) {
        return decoded.values.expand((v) => v is List ? v : [v]).join(', ');
      }
      return body;
    } catch (_) {
      return body;
    }
  }
}
