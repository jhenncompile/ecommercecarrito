import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../models/order_model.dart';
import '../repositories/order_repository.dart';
import '../../gestion_pago/repositories/payment_repository.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import 'package:open_filex/open_filex.dart';
import 'dart:convert';
import '../../core/widgets/feedback/app_toast.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});

  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> {
  List<OrderModel> _orders = [];
  bool _isLoading = true;
  final OrderRepository _orderRepository = OrderRepository();
  final PaymentRepository _paymentRepository = PaymentRepository();
  final ApiClient _apiClient = ApiClient();

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    setState(() => _isLoading = true);
    try {
      // Usamos global_list para ver pedidos de todas las tiendas
      final orders = await _orderRepository.fetchGlobalOrders();
      setState(() {
        _orders = orders;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppDashboardLayout(
      brandName: 'MiQhatu',
      userName: 'Cliente',
      sidebarItems: [
        AppSidebarItem(
          icon: Icons.store,
          label: 'Explorar Tiendas',
          onTap: () => Navigator.pushReplacementNamed(context, '/tiendas'),
        ),
        AppSidebarItem(
          icon: Icons.shopping_bag_outlined,
          label: 'Mis Pedidos',
          isActive: true,
          onTap: () => Navigator.pushReplacementNamed(context, '/pedidos'),
        ),
        AppSidebarItem(
          icon: Icons.logout,
          label: 'Salir',
          isLogout: true,
          onTap: () => Navigator.pushReplacementNamed(context, '/login'),
        ),
      ],
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Mis Pedidos', style: AppTextStyles.h1),
          const SizedBox(height: 5),
          Text('Historial de compras en todas tus tiendas', style: AppTextStyles.subtitle),
          const SizedBox(height: 30),
          if (_isLoading)
            const Center(child: CircularProgressIndicator(color: AppColors.accentTeal))
          else if (_orders.isEmpty)
            const Center(child: Text('Aún no tienes pedidos realizados.'))
          else              ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _orders.length,
              itemBuilder: (context, index) {
                final order = _orders[index];
                return _OrderCard(
                  order: order,
                  onReload: _loadOrders,
                  apiClient: _apiClient,
                  paymentRepository: _paymentRepository,
                );
              },
            ),
        ],
      ),
    );
  }
}

class _OrderCard extends StatefulWidget {
  final OrderModel order;
  final VoidCallback onReload;
  final ApiClient apiClient;
  final PaymentRepository paymentRepository;

  const _OrderCard({
    required this.order,
    required this.onReload,
    required this.apiClient,
    required this.paymentRepository,
  });

  @override
  State<_OrderCard> createState() => _OrderCardState();
}

class _OrderCardState extends State<_OrderCard> {
  bool _isExpanded = false;

  Color _getStatusColor(String status) {
    switch (status.toUpperCase()) {
      case 'ENTREGADO': return AppColors.success;
      case 'ENVIADO': return AppColors.success;
      case 'PAGADO': return AppColors.info;
      case 'PROCESADO': return AppColors.warning;
      case 'PENDIENTE': return AppColors.primary;
      case 'CANCELADO': return AppColors.danger;
      default: return AppColors.textMuted;
    }
  }

  Color _getLabelColor(String currentStatus, String targetState) {
    final statusUpper = currentStatus.toUpperCase();
    final allStates = ['PENDIENTE', 'PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO'];
    if (statusUpper == 'CANCELADO') return AppColors.textMuted;
    
    int currentIndex = allStates.indexOf(statusUpper);
    int targetIndex = allStates.indexOf(targetState);
    if (currentIndex == -1 || targetIndex == -1) return AppColors.textMuted;
    
    if (targetIndex <= currentIndex) {
      switch (targetState) {
        case 'PENDIENTE': return AppColors.primary;
        case 'PAGADO': return AppColors.info;
        case 'PROCESADO': return AppColors.warning;
        case 'ENVIADO':
        case 'ENTREGADO': return AppColors.success;
      }
    }
    return AppColors.textMuted;
  }

  Widget _buildProgressBar(String currentStatus) {
    final statusUpper = currentStatus.toUpperCase();
    final allStates = ['PENDIENTE', 'PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO'];
    
    bool isPast(String state) {
      if (statusUpper == 'CANCELADO') return false;
      int currentIndex = allStates.indexOf(statusUpper);
      int targetIndex = allStates.indexOf(state);
      if (currentIndex == -1 || targetIndex == -1) return false;
      return targetIndex <= currentIndex;
    }

    return Container(
      height: 6,
      decoration: BoxDecoration(
        color: AppColors.surface2,
        borderRadius: BorderRadius.circular(3),
      ),
      child: Row(
        children: allStates.map((state) {
          Color color = Colors.transparent;
          if (isPast(state)) {
            switch (state) {
              case 'PENDIENTE': color = AppColors.primary; break;
              case 'PAGADO': color = AppColors.info; break;
              case 'PROCESADO': color = AppColors.warning; break;
              case 'ENVIADO':
              case 'ENTREGADO': color = AppColors.success; break;
            }
          }
          return Expanded(
            child: Container(
              color: color,
            ),
          );
        }).toList(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final order = widget.order;
    final dateStr = DateFormat('dd/MM/yyyy HH:mm').format(order.fecha);
    
    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: _isExpanded ? AppColors.borderHighlight : AppColors.border),
      ),
      child: Column(
        children: [
          InkWell(
            onTap: () => setState(() => _isExpanded = !_isExpanded),
            borderRadius: BorderRadius.circular(15),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _getStatusColor(order.estado).withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(Icons.receipt_long, color: _getStatusColor(order.estado)),
                  ),
                  const SizedBox(width: 20),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(order.numero, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                        const SizedBox(height: 4),
                        Text('Tienda: ${order.tenantName ?? 'General'}', style: const TextStyle(color: AppColors.textMuted, fontSize: 13)),
                        Text(dateStr, style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
                        const SizedBox(height: 10),
                        // Etiquetas de progreso y barra
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('PENDIENTE', style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: _getLabelColor(order.estado, 'PENDIENTE'))),
                            Text('PAGADO', style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: _getLabelColor(order.estado, 'PAGADO'))),
                            Text('PROCESADO', style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: _getLabelColor(order.estado, 'PROCESADO'))),
                            Text('ENVIADO', style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: _getLabelColor(order.estado, 'ENVIADO'))),
                            Text('ENTREGADO', style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: _getLabelColor(order.estado, 'ENTREGADO'))),
                          ],
                        ),
                        const SizedBox(height: 4),
                        _buildProgressBar(order.estado),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: _getStatusColor(order.estado).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: _getStatusColor(order.estado)),
                          ),
                          child: Text(
                            order.estado,
                            style: TextStyle(color: _getStatusColor(order.estado), fontSize: 10, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 15),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text('BS. ${order.total}', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: AppColors.primaryDark)),
                      const SizedBox(height: 10),
                      if (order.estado.toUpperCase() == 'PENDIENTE')
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primaryDark,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                            textStyle: const TextStyle(fontSize: 12),
                          ),
                          onPressed: () async {
                            AppToast.showInfo(context, 'Iniciando pago...');
                            final success = await widget.paymentRepository.processPaymentSheet(order.id);
                            if (success) {
                              AppToast.showSuccess(context, '¡Pago completado!');
                              widget.onReload();
                            }
                          },
                          child: const Text('Pagar ahora'),
                        ),
                      if (order.estado.toUpperCase() == 'PAGADO')
                        OutlinedButton(
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                            textStyle: const TextStyle(fontSize: 12),
                          ),
                          onPressed: () async {
                            AppToast.showInfo(context, 'Descargando factura...');
                            try {
                              // Usamos override de tenant si existe
                              final res = await widget.apiClient.get('${ApiConstants.mainBaseUrl}/facturas/?pedido=${order.id}', requiresAuth: true, includeTenantHost: true, tenantHostOverride: order.schemaName);
                              if (res.statusCode == 200) {
                                final data = jsonDecode(res.body);
                                final list = data['results'] ?? data;
                                if (list.isNotEmpty) {
                                  final factura = list[0];
                                  final nro = factura['nro'].toString();
                                  
                                  final pdfRes = await widget.apiClient.get('${ApiConstants.mainBaseUrl}/facturas/$nro/descargar_pdf/', requiresAuth: true, includeTenantHost: true, tenantHostOverride: order.schemaName);
                                  
                                  if (pdfRes.statusCode == 200) {
                                    final bytes = pdfRes.bodyBytes;
                                    final dir = await getApplicationDocumentsDirectory();
                                    final file = File('${dir.path}/factura_$nro.pdf');
                                    await file.writeAsBytes(bytes);
                                    
                                    AppToast.showSuccess(context, 'Factura descargada');
                                    OpenFilex.open(file.path);
                                  } else {
                                    throw Exception('Error al descargar');
                                  }
                                } else {
                                  AppToast.showInfo(context, 'Factura en proceso. Intenta más tarde.');
                                }
                              }
                            } catch (e) {
                              AppToast.showError(context, 'Error al descargar factura');
                            }
                          },
                          child: const Text('Factura'),
                        ),
                      if (order.estado.toUpperCase() == 'ENVIADO')
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.success,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                            textStyle: const TextStyle(fontSize: 12),
                          ),
                          onPressed: () async {
                            final confirm = await showDialog<bool>(
                              context: context,
                              builder: (c) => AlertDialog(
                                title: const Text('Confirmar Entrega'),
                                content: const Text('¿Confirmas que has recibido tu pedido?'),
                                actions: [
                                  TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancelar')),
                                  ElevatedButton(
                                    style: ElevatedButton.styleFrom(backgroundColor: AppColors.success),
                                    onPressed: () => Navigator.pop(c, true),
                                    child: const Text('Confirmar', style: TextStyle(color: Colors.white)),
                                  ),
                                ],
                              ),
                            );
                            if (confirm == true) {
                              AppToast.showInfo(context, 'Actualizando estado...');
                              try {
                                // Asegurar que el host sea el dominio completo (ej: gerlexxtech2.157.x.x.nip.io)
                                // Si schemaName ya tiene un punto, es el dominio completo; si no, construir uno.
                                final rawSchema = order.schemaName ?? '';
                                final tenantHost = rawSchema.contains('.')
                                    ? rawSchema
                                    : '$rawSchema.${ApiConstants.vpsIp}.nip.io';

                                final res = await widget.apiClient.post(
                                  '${ApiConstants.mainBaseUrl}/pedidos/${order.id}/cambiar-estado/',
                                  {'estado': 'ENTREGADO'},
                                  requiresAuth: true,
                                  includeTenantHost: true,
                                  tenantHostOverride: tenantHost,
                                );
                                if (res.statusCode == 200 || res.statusCode == 201) {
                                  AppToast.showSuccess(context, '¡Pedido finalizado con éxito!');
                                  widget.onReload();
                                } else {
                                  print('Error en cambiar-estado: ${res.statusCode} - ${res.body}');
                                  AppToast.showError(context, 'Error al confirmar entrega. (${res.statusCode})');
                                }
                              } catch(e) {
                                print('Catch error en cambiar-estado: $e');
                                AppToast.showError(context, 'Error de red al confirmar entrega.');
                              }
                            }
                          },
                          child: const Text('Marcar como Entregado'),
                        ),
                      const SizedBox(height: 10),
                      Icon(_isExpanded ? Icons.expand_less : Icons.expand_more, color: AppColors.textMuted),
                    ],
                  ),
                ],
              ),
            ),
          ),
          if (_isExpanded)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
              decoration: const BoxDecoration(
                border: Border(top: BorderSide(color: AppColors.border)),
                color: AppColors.bgSurface,
                borderRadius: BorderRadius.only(bottomLeft: Radius.circular(15), bottomRight: Radius.circular(15)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Productos del Pedido:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.textSecondary)),
                  const SizedBox(height: 10),
                  if (order.items != null && order.items!.isNotEmpty)
                    ...order.items!.map((item) => Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(child: Text('${item.cantidad}x ${item.producto.nombre}', style: const TextStyle(fontSize: 13))),
                          Text('Bs. ${item.subtotal}', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                        ],
                      ),
                    )).toList()
                  else
                    const Text('No se encontraron detalles de productos.', style: TextStyle(fontSize: 13, color: AppColors.textMuted)),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

