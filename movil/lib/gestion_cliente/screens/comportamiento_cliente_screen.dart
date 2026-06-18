// movil/lib/gestion_cliente/screens/comportamiento_cliente_screen.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/network/api_client.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';

// ── Modelos de respuesta ────────────────────────────────────────
class _ComportamientoData {
  final List<_ProductoTop> productosTop;
  final double ticketPromedio;
  final double totalVentas;
  final int totalPedidos;
  final List<_VentaDia> ventasPorDia;

  const _ComportamientoData({
    required this.productosTop,
    required this.ticketPromedio,
    required this.totalVentas,
    required this.totalPedidos,
    required this.ventasPorDia,
  });
}

class _ProductoTop {
  final String nombre;
  final int cantidad;
  final double total;
  const _ProductoTop({required this.nombre, required this.cantidad, required this.total});
}

class _VentaDia {
  final String fecha;
  final double monto;
  const _VentaDia({required this.fecha, required this.monto});
}

// ── Pantalla ────────────────────────────────────────────────────
class ComportamientoClienteScreen extends StatefulWidget {
  const ComportamientoClienteScreen({Key? key}) : super(key: key);

  @override
  State<ComportamientoClienteScreen> createState() =>
      _ComportamientoClienteScreenState();
}

class _ComportamientoClienteScreenState
    extends State<ComportamientoClienteScreen> {
  final ApiClient _api = ApiClient();
  final AuthRepository _authRepo = AuthRepository();

  String _storeName = '';
  String _periodo = 'mes'; // 'semana' | 'mes' | 'año'
  bool _isLoading = true;
  String? _error;
  _ComportamientoData? _data;

  @override
  void initState() {
    super.initState();
    _inicializar();
  }

  Future<void> _inicializar() async {
    final schema = await _authRepo.getSchemaName();
    setState(() => _storeName = schema ?? '');
    await _cargar();
  }

  Future<void> _cargar() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final res = await _api.get(
        '/reportes/comportamiento/?periodo=$_periodo',
        requiresAuth: true,
        includeTenantHost: true,
      );
      if (res.statusCode == 200) {
        final json = jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
        _data = _parseData(json);
      } else {
        // Si el endpoint no existe aún → datos simulados para prototipo
        _data = _datosSimulados();
      }
    } catch (_) {
      _data = _datosSimulados();
    } finally {
      setState(() => _isLoading = false);
    }
  }

  _ComportamientoData _parseData(Map<String, dynamic> json) {
    final productos = (json['productos_top'] as List? ?? [])
        .map((e) => _ProductoTop(
              nombre: e['nombre'] ?? '',
              cantidad: e['cantidad'] ?? 0,
              total: (e['total'] as num).toDouble(),
            ))
        .toList();
    final ventasDia = (json['ventas_por_dia'] as List? ?? [])
        .map((e) => _VentaDia(
              fecha: e['fecha'] ?? '',
              monto: (e['monto'] as num).toDouble(),
            ))
        .toList();
    return _ComportamientoData(
      productosTop: productos,
      ticketPromedio: (json['ticket_promedio'] as num?)?.toDouble() ?? 0,
      totalVentas: (json['total_ventas'] as num?)?.toDouble() ?? 0,
      totalPedidos: json['total_pedidos'] ?? 0,
      ventasPorDia: ventasDia,
    );
  }

  // Datos de demostración mientras el endpoint se implementa
  _ComportamientoData _datosSimulados() {
    return _ComportamientoData(
      productosTop: [
        const _ProductoTop(nombre: 'Arroz 1 kg', cantidad: 85, total: 425),
        const _ProductoTop(nombre: 'Aceite girasol', cantidad: 60, total: 540),
        const _ProductoTop(nombre: 'Azucar 2 kg', cantidad: 50, total: 350),
        const _ProductoTop(nombre: 'Harina 1 kg', cantidad: 42, total: 210),
        const _ProductoTop(nombre: 'Fideos', cantidad: 38, total: 190),
      ],
      ticketPromedio: 87.50,
      totalVentas: 8750,
      totalPedidos: 100,
      ventasPorDia: [
        const _VentaDia(fecha: 'Lun', monto: 1200),
        const _VentaDia(fecha: 'Mar', monto: 980),
        const _VentaDia(fecha: 'Mie', monto: 1450),
        const _VentaDia(fecha: 'Jue', monto: 870),
        const _VentaDia(fecha: 'Vie', monto: 1600),
        const _VentaDia(fecha: 'Sab', monto: 1900),
        const _VentaDia(fecha: 'Dom', monto: 750),
      ],
    );
  }

  // ── Construir barra de barras simple ────────────────────────
  Widget _buildBarChart(List<_VentaDia> dias) {
    if (dias.isEmpty) return const SizedBox.shrink();
    final maxMonto = dias.map((d) => d.monto).reduce((a, b) => a > b ? a : b);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Ventas por Dia', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF0F172A))),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: dias.map((d) {
              final pct = maxMonto > 0 ? d.monto / maxMonto : 0.0;
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: Column(
                    children: [
                      Text(
                        'Bs.${d.monto.toStringAsFixed(0)}',
                        style: const TextStyle(fontSize: 8, color: Color(0xFF64748B)),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 4),
                      AnimatedContainer(
                        duration: const Duration(milliseconds: 600),
                        height: (140 * pct).clamp(4.0, 140.0),
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            begin: Alignment.bottomCenter,
                            end: Alignment.topCenter,
                            colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                          ),
                          borderRadius: BorderRadius.circular(6),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(d.fecha, style: const TextStyle(fontSize: 10, color: Color(0xFF64748B))),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  // ── Tarjeta KPI ───────────────────────────────────────────────
  Widget _buildKpi(String titulo, String valor, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 6)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: 20, color: color),
            const SizedBox(height: 8),
            Text(valor, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
            const SizedBox(height: 2),
            Text(titulo, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
          ],
        ),
      ),
    );
  }

  // ── Fila de productos top ─────────────────────────────────────
  Widget _buildProductoTop(_ProductoTop p, int rank, double maxCantidad) {
    final pct = maxCantidad > 0 ? p.cantidad / maxCantidad : 0.0;
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Container(
            width: 26,
            height: 26,
            decoration: BoxDecoration(
              color: rank == 1
                  ? const Color(0xFFF59E0B)
                  : rank == 2
                      ? const Color(0xFF94A3B8)
                      : const Color(0xFFCD7C2F),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text('$rank', style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(p.nombre, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13), overflow: TextOverflow.ellipsis),
                    ),
                    Text('${p.cantidad} und.', style: const TextStyle(fontSize: 12, color: Color(0xFF6366F1), fontWeight: FontWeight.bold)),
                  ],
                ),
                const SizedBox(height: 4),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: pct,
                    backgroundColor: const Color(0xFFF1F5F9),
                    valueColor: const AlwaysStoppedAnimation(Color(0xFF6366F1)),
                    minHeight: 6,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Text('Bs.${p.total.toStringAsFixed(0)}', style: const TextStyle(fontSize: 12, color: Color(0xFF10B981), fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  List<AppSidebarItem> get _sidebarItems => [
        AppSidebarItem(icon: Icons.dashboard, label: 'Panel', onTap: () => Navigator.pushReplacementNamed(context, '/dashboard')),
        AppSidebarItem(icon: Icons.inventory_2, label: 'Productos', onTap: () => Navigator.pushReplacementNamed(context, '/productos')),
        AppSidebarItem(icon: Icons.shopping_cart, label: 'Ventas', onTap: () => Navigator.pushReplacementNamed(context, '/ventas')),
        AppSidebarItem(icon: Icons.people, label: 'Clientes', onTap: () => Navigator.pushReplacementNamed(context, '/clientes')),
        AppSidebarItem(icon: Icons.bar_chart, label: 'Reportes', onTap: () => Navigator.pushReplacementNamed(context, '/reportes')),
        AppSidebarItem(icon: Icons.insights, label: 'Comportamiento', isActive: true, onTap: () {}),
        AppSidebarItem(icon: Icons.trending_up, label: 'Predicciones', onTap: () => Navigator.pushReplacementNamed(context, '/predicciones')),
        AppSidebarItem(icon: Icons.alarm, label: 'Recordatorios', onTap: () => Navigator.pushReplacementNamed(context, '/recordatorios')),
        AppSidebarItem(icon: Icons.backup, label: 'Backup', onTap: () => Navigator.pushReplacementNamed(context, '/backup')),
        AppSidebarItem(icon: Icons.settings, label: 'Configuracion', onTap: () => Navigator.pushReplacementNamed(context, '/configuracion')),
        AppSidebarItem(icon: Icons.logout, label: 'Salir', isLogout: true, onTap: () => Navigator.pushReplacementNamed(context, '/login')),
      ];

  @override
  Widget build(BuildContext context) {
    return AppDashboardLayout(
      brandName: 'MiQhatu',
      tenantValue: _storeName,
      userName: '',
      sidebarItems: _sidebarItems,
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF6366F1)))
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
              : RefreshIndicator(
              onRefresh: _cargar,
              color: const Color(0xFF6366F1),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // ── Header ──
                    Row(
                      children: [
                        const Icon(Icons.insights, size: 22, color: Color(0xFF6366F1)),
                        const SizedBox(width: 8),
                        Text('Comportamiento del Cliente', style: AppTextStyles.h1.copyWith(fontSize: 20)),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text('Analisis de patrones de compra', style: AppTextStyles.subtitle),
                    const SizedBox(height: 16),

                    // ── Filtro de periodo ──
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: ['semana', 'mes', 'año'].map((p) {
                          final labels = {'semana': 'Esta Semana', 'mes': 'Este Mes', 'año': 'Este Año'};
                          return Padding(
                            padding: const EdgeInsets.only(right: 8),
                            child: FilterChip(
                              label: Text(labels[p]!),
                              selected: _periodo == p,
                              onSelected: (_) {
                                setState(() => _periodo = p);
                                _cargar();
                              },
                              selectedColor: const Color(0xFF6366F1).withOpacity(0.15),
                              checkmarkColor: const Color(0xFF6366F1),
                              labelStyle: TextStyle(
                                color: _periodo == p ? const Color(0xFF6366F1) : Colors.grey,
                                fontWeight: FontWeight.w600,
                                fontSize: 12,
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                    const SizedBox(height: 16),

                    if (_data != null) ...[
                      // ── KPIs ──
                      Row(
                        children: [
                          _buildKpi('Total Ventas', 'Bs.${_data!.totalVentas.toStringAsFixed(0)}', Icons.attach_money, const Color(0xFF10B981)),
                          const SizedBox(width: 10),
                          _buildKpi('Total Pedidos', '${_data!.totalPedidos}', Icons.shopping_bag_outlined, const Color(0xFF6366F1)),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          _buildKpi('Ticket Promedio', 'Bs.${_data!.ticketPromedio.toStringAsFixed(2)}', Icons.receipt_long_outlined, const Color(0xFFF59E0B)),
                          const SizedBox(width: 10),
                          _buildKpi('Productos Top', '${_data!.productosTop.length}', Icons.star_outline, const Color(0xFFEF4444)),
                        ],
                      ),
                      const SizedBox(height: 20),

                      // ── Grafico de barras ──
                      _buildBarChart(_data!.ventasPorDia),
                      const SizedBox(height: 20),

                      // ── Productos mas vendidos ──
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2))],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.emoji_events_outlined, size: 18, color: Color(0xFFF59E0B)),
                                const SizedBox(width: 6),
                                const Text('Productos mas Vendidos', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF0F172A))),
                              ],
                            ),
                            const SizedBox(height: 14),
                            if (_data!.productosTop.isEmpty)
                              const Center(child: Text('Sin datos suficientes', style: TextStyle(color: Colors.grey)))
                            else
                              ...() {
                                final max = _data!.productosTop[0].cantidad.toDouble();
                                return _data!.productosTop.asMap().entries.map((e) {
                                  return _buildProductoTop(e.value, e.key + 1, max);
                                }).toList();
                              }(),
                          ],
                        ),
                      ),
                      const SizedBox(height: 20),

                      // ── Nota de datos simulados ──
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEF3C7),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: const Color(0xFFF59E0B)),
                        ),
                        child: Row(
                          children: const [
                            Icon(Icons.info_outline, size: 16, color: Color(0xFFD97706)),
                            SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'Datos de demostracion. Conectar con /api/reportes/comportamiento/ para datos reales.',
                                style: TextStyle(fontSize: 12, color: Color(0xFF92400E)),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
    );
  }
}
