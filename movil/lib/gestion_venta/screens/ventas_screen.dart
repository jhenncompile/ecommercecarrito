import 'package:flutter/material.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';
import '../repositories/venta_repository.dart';
import '../models/pedido.dart';
import '../widgets/pedido_detail_bottom_sheet.dart';
import 'dart:convert';

class VentasScreen extends StatefulWidget {
  const VentasScreen({super.key});

  @override
  State<VentasScreen> createState() => _VentasScreenState();
}

class _VentasScreenState extends State<VentasScreen> {
  String _storeName = 'Cargando...';
  String _userName = 'Admin';
  final AuthRepository _authRepository = AuthRepository();
  final VentaRepository _ventaRepository = VentaRepository();

  bool _isLoading = false;
  String? _error;
  List<Pedido> _pedidos = [];
  List<Pedido> _filteredPedidos = [];
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _inicializar();
    _cargarPedidos();
  }

  Future<void> _inicializar() async {
    final schemaName = await _authRepository.getSchemaName();
    String decodedUser = 'Admin';
    final token = await _authRepository.getAccessToken();
    if (token != null) {
      final payload = _decodeJwt(token);
      if (payload != null) {
        decodedUser = payload['full_name'] ?? payload['username'] ?? 'Admin';
      }
    }
    if (mounted) {
      setState(() {
        _storeName = _formatStoreName(schemaName ?? '');
        _userName = decodedUser;
      });
    }
  }

  Future<void> _cargarPedidos() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final data = await _ventaRepository.getPedidos();
      if (mounted) {
        setState(() {
          _pedidos = data;
          _filtrarPedidos();
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Error al cargar ventas: $e';
          _isLoading = false;
        });
      }
    }
  }

  void _filtrarPedidos() {
    if (_searchQuery.isEmpty) {
      _filteredPedidos = List.from(_pedidos);
    } else {
      final query = _searchQuery.toLowerCase();
      _filteredPedidos = _pedidos.where((p) {
        return p.clienteNombre.toLowerCase().contains(query) ||
               p.id.toString().contains(query);
      }).toList();
    }
  }

  String _formatStoreName(String schema) {
    if (schema.isEmpty) return 'Mi Tienda';
    return schema.split(RegExp(r'[x_]+')).map((word) {
      if (word.isEmpty) return '';
      return word[0].toUpperCase() + word.substring(1).toLowerCase();
    }).join(' ');
  }

  Map<String, dynamic>? _decodeJwt(String token) {
    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;
      var payload = parts[1];
      while (payload.length % 4 != 0) {
        payload += '=';
      }
      return jsonDecode(utf8.decode(base64Url.decode(payload)));
    } catch (_) {
      return null;
    }
  }

  Map<String, List<Pedido>> _agruparPorFecha(List<Pedido> pedidos) {
    final Map<String, List<Pedido>> agrupados = {};
    for (var p in pedidos) {
      final dateStr = p.fechaCreacion.split('T').first;
      if (!agrupados.containsKey(dateStr)) agrupados[dateStr] = [];
      agrupados[dateStr]!.add(p);
    }
    return agrupados;
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'PENDIENTE': return Colors.orange;
      case 'PAGADO': return AppColors.tealLight;
      case 'PROCESADO': return Colors.blue;
      case 'ENVIADO': return Colors.orange;
      case 'ENTREGADO': return AppColors.success;
      case 'CANCELADO': return AppColors.danger;
      default: return AppColors.textMuted;
    }
  }

  void _mostrarDetalle(Pedido pedido) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => PedidoDetailBottomSheet(
        pedido: pedido,
        onStatusChanged: _cargarPedidos,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Agrupar y ordenar las fechas de mayor a menor
    final agrupados = _agruparPorFecha(_filteredPedidos);
    final fechas = agrupados.keys.toList()..sort((a, b) => b.compareTo(a));

    return AppDashboardLayout(
      brandName: 'MiQhatu',
      tenantValue: _storeName,
      userName: _userName,
      sidebarItems: [
        AppSidebarItem(icon: Icons.dashboard, label: 'Panel', onTap: () => Navigator.pushReplacementNamed(context, '/dashboard')),
        AppSidebarItem(icon: Icons.inventory_2, label: 'Productos', onTap: () => Navigator.pushReplacementNamed(context, '/productos')),
        AppSidebarItem(icon: Icons.category, label: 'Categorías', onTap: () => Navigator.pushReplacementNamed(context, '/categorias')),
        AppSidebarItem(icon: Icons.list_alt, label: 'Inventario', onTap: () => Navigator.pushReplacementNamed(context, '/inventario')),
        AppSidebarItem(icon: Icons.shopping_cart, label: 'Ventas', isActive: true, onTap: () => Navigator.pushReplacementNamed(context, '/ventas')),
        AppSidebarItem(icon: Icons.people, label: 'Clientes', onTap: () => Navigator.pushReplacementNamed(context, '/clientes')),
        AppSidebarItem(icon: Icons.bar_chart, label: 'Reportes', onTap: () => Navigator.pushReplacementNamed(context, '/reportes')),
        AppSidebarItem(icon: Icons.trending_up, label: 'Predicciones', onTap: () => Navigator.pushReplacementNamed(context, '/predicciones')),
        AppSidebarItem(icon: Icons.settings, label: 'Configuración', onTap: () => Navigator.pushReplacementNamed(context, '/configuracion')),
        AppSidebarItem(icon: Icons.logout, label: 'Salir', isLogout: true, onTap: () async {
          await _authRepository.logout();
          if (!context.mounted) return;
          Navigator.pushReplacementNamed(context, '/login');
        }),
      ],
      body: RefreshIndicator(
        onRefresh: _cargarPedidos,
        color: AppColors.primaryDark,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Text('Ventas y Pedidos', style: AppTextStyles.h1),
              const SizedBox(height: 5),
              Text('Administra los pedidos de tus clientes.', style: AppTextStyles.subtitle),
              const SizedBox(height: 20),

              // Buscador
              TextField(
                decoration: InputDecoration(
                  hintText: 'Buscar por número (#) o cliente...',
                  prefixIcon: const Icon(Icons.search, color: AppColors.textMuted),
                  filled: true,
                  fillColor: AppColors.bgCard,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: AppColors.border),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: AppColors.border),
                  ),
                ),
                onChanged: (val) {
                  setState(() {
                    _searchQuery = val;
                    _filtrarPedidos();
                  });
                },
              ),
              const SizedBox(height: 20),

              if (_isLoading && _pedidos.isEmpty)
                const Center(child: Padding(padding: EdgeInsets.all(40), child: CircularProgressIndicator()))
              else if (_error != null)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(color: AppColors.danger.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
                  child: Row(
                    children: [
                      const Icon(Icons.error, color: AppColors.danger),
                      const SizedBox(width: 10),
                      Expanded(child: Text(_error!, style: const TextStyle(color: AppColors.danger))),
                    ],
                  ),
                )
              else if (_filteredPedidos.isEmpty)
                Center(
                  child: Padding(
                    padding: const EdgeInsets.all(40),
                    child: Column(
                      children: [
                        const Icon(Icons.shopping_cart_outlined, size: 60, color: AppColors.textMuted),
                        const SizedBox(height: 10),
                        Text('No se encontraron ventas', style: AppTextStyles.h3.copyWith(color: AppColors.textMuted)),
                      ],
                    ),
                  ),
                )
              else
                // Lista agrupada por fecha
                ...fechas.map((fecha) {
                  final items = agrupados[fecha]!;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.calendar_today, size: 16, color: AppColors.textMuted),
                            const SizedBox(width: 8),
                            Text(fecha, style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textMuted)),
                          ],
                        ),
                        const Divider(),
                        ...items.map((pedido) => Card(
                          margin: const EdgeInsets.only(bottom: 10),
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                            side: const BorderSide(color: AppColors.border),
                          ),
                          child: InkWell(
                            onTap: () => _mostrarDetalle(pedido),
                            borderRadius: BorderRadius.circular(12),
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text('#${pedido.id} - ${pedido.clienteNombre}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: _getStatusColor(pedido.estado).withOpacity(0.1),
                                          borderRadius: BorderRadius.circular(12),
                                          border: Border.all(color: _getStatusColor(pedido.estado)),
                                        ),
                                        child: Text(
                                          pedido.estado,
                                          style: TextStyle(color: _getStatusColor(pedido.estado), fontSize: 10, fontWeight: FontWeight.bold),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 10),
                                  Text(
                                    pedido.items.isNotEmpty
                                        ? pedido.items.map((i) => '${i.productoNombre} (x${i.cantidad})').join(', ')
                                        : '${pedido.cantidadItems} items',
                                    style: const TextStyle(color: AppColors.textGray, fontSize: 13),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 10),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text('Bs. ${pedido.totalPedido}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppColors.primaryDark)),
                                      const Row(
                                        children: [
                                          Icon(Icons.remove_red_eye, size: 16, color: AppColors.accentTeal),
                                          SizedBox(width: 4),
                                          Text('Ver Detalle', style: TextStyle(color: AppColors.accentTeal, fontWeight: FontWeight.bold)),
                                        ],
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ),
                        )),
                      ],
                    ),
                  );
                }),
            ],
          ),
        ),
      ),
    );
  }
}

