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
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _orders.length,
              itemBuilder: (context, index) {
                final order = _orders[index];
                return _buildOrderCard(order);
              },
            ),
        ],
      ),
    );
  }

  Widget _buildOrderCard(OrderModel order) {
    final dateStr = DateFormat('dd/MM/yyyy HH:mm').format(order.fecha);
    
    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: AppColors.border),
      ),
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
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('BS. ${order.total}', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: AppColors.primaryDark)),
              const SizedBox(height: 8),
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
                    final success = await _paymentRepository.processPaymentSheet(order.id);
                    if (success) {
                      AppToast.showSuccess(context, '¡Pago completado!');
                      _loadOrders();
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
                      // Buscar factura
                      final res = await _apiClient.get('${ApiConstants.mainBaseUrl}/facturas/?pedido=${order.id}', requiresAuth: true, includeTenantHost: true);
                      if (res.statusCode == 200) {
                        final data = jsonDecode(res.body);
                        final list = data['results'] ?? data;
                        if (list.isNotEmpty) {
                          final factura = list[0];
                          final nro = factura['nro'].toString();
                          
                          // Descargar PDF
                          final pdfRes = await _apiClient.get('${ApiConstants.mainBaseUrl}/facturas/$nro/descargar_pdf/', requiresAuth: true, includeTenantHost: true);
                          
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
            ],
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toUpperCase()) {
      case 'PAGADO': return AppColors.success;
      case 'PENDIENTE': return AppColors.warning;
      case 'CANCELADO': return AppColors.danger;
      default: return AppColors.textMuted;
    }
  }
}
