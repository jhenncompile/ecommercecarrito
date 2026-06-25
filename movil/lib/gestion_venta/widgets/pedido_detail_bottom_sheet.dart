import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../models/pedido.dart';
import '../repositories/venta_repository.dart';

class PedidoDetailBottomSheet extends StatefulWidget {
  final Pedido pedido;
  final VoidCallback onStatusChanged;

  const PedidoDetailBottomSheet({
    super.key,
    required this.pedido,
    required this.onStatusChanged,
  });

  @override
  State<PedidoDetailBottomSheet> createState() => _PedidoDetailBottomSheetState();
}

class _PedidoDetailBottomSheetState extends State<PedidoDetailBottomSheet> {
  final VentaRepository _ventaRepository = VentaRepository();
  bool _isLoading = false;
  late String _currentStatus;

  final List<String> _estados = ['PENDIENTE', 'PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO', 'CANCELADO'];

  @override
  void initState() {
    super.initState();
    _currentStatus = widget.pedido.estado;
  }

  Future<void> _cambiarEstado(String nuevoEstado) async {
    setState(() => _isLoading = true);
    try {
      await _ventaRepository.cambiarEstado(widget.pedido.id, nuevoEstado);
      setState(() {
        _currentStatus = nuevoEstado;
      });
      widget.onStatusChanged();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Estado actualizado'), backgroundColor: AppColors.success),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.danger),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
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

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        top: 20,
        left: 20,
        right: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      decoration: const BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Pedido #${widget.pedido.id}', style: AppTextStyles.h2),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getStatusColor(_currentStatus).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _getStatusColor(_currentStatus)),
                  ),
                  child: Text(
                    _currentStatus,
                    style: TextStyle(
                      color: _getStatusColor(_currentStatus),
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Cliente Info
            const Text('Información del Cliente', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.person, color: AppColors.textMuted, size: 20),
                const SizedBox(width: 8),
                Text(widget.pedido.clienteNombre, style: AppTextStyles.body),
              ],
            ),
            const SizedBox(height: 5),
            Row(
              children: [
                const Icon(Icons.email, color: AppColors.textMuted, size: 20),
                const SizedBox(width: 8),
                Text(widget.pedido.clienteEmail.isNotEmpty ? widget.pedido.clienteEmail : 'Sin correo', style: AppTextStyles.body),
              ],
            ),
            const SizedBox(height: 5),
            Row(
              children: [
                const Icon(Icons.calendar_today, color: AppColors.textMuted, size: 20),
                const SizedBox(width: 8),
                Text(widget.pedido.fechaCreacion.split('T').first, style: AppTextStyles.body),
              ],
            ),
            const Divider(height: 30),

            // Items
            const Text('Productos', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 10),
            ...widget.pedido.items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${item.cantidad}x ', style: const TextStyle(fontWeight: FontWeight.bold)),
                  Expanded(child: Text(item.productoNombre)),
                  Text('Bs. ${item.subtotal}', style: const TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
            )),
            
            const Divider(height: 30),
            
            // Totales
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('TOTAL', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                Text('Bs. ${widget.pedido.totalPedido}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppColors.primaryDark)),
              ],
            ),
            
            if (widget.pedido.observaciones != null && widget.pedido.observaciones!.isNotEmpty) ...[
              const SizedBox(height: 20),
              const Text('Observaciones', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 5),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(widget.pedido.observaciones!, style: const TextStyle(fontStyle: FontStyle.italic)),
              ),
            ],

            const SizedBox(height: 30),
            const Text('Cambiar Estado', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 10),
            
            if (_isLoading)
              const Center(child: CircularProgressIndicator())
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _estados.map((estado) {
                  final isCurrent = estado == _currentStatus;
                  return InkWell(
                    onTap: isCurrent ? null : () => _cambiarEstado(estado),
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: isCurrent ? _getStatusColor(estado) : Colors.transparent,
                        border: Border.all(color: _getStatusColor(estado)),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        estado,
                        style: TextStyle(
                          color: isCurrent ? Colors.white : _getStatusColor(estado),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),

            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: AppButton.secondary(
                label: 'Cerrar',
                onPressed: () => Navigator.pop(context),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
