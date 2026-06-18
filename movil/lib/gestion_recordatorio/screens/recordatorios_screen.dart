// movil/lib/gestion_recordatorio/screens/recordatorios_screen.dart
import 'package:flutter/material.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/widgets/layout/app_dashboard_layout.dart';
import '../../core/widgets/layout/app_sidebar.dart';
import '../../gestion_usuario/repositories/auth_repository.dart';
import '../models/recordatorio_model.dart';
import '../repositories/recordatorio_repository.dart';

// ── Configuración visual por tipo ──────────────────────────────
class _TipoConfig {
  final String label;
  final Color color;
  final Color bgColor;
  final IconData icon;

  const _TipoConfig({
    required this.label,
    required this.color,
    required this.bgColor,
    required this.icon,
  });
}

const Map<String, _TipoConfig> _tipoConfig = {
  'TAREA': _TipoConfig(
    label: 'Tarea',
    color: Color(0xFF6366F1),
    bgColor: Color(0xFFEEF2FF),
    icon: Icons.task_alt,
  ),
  'PAGO': _TipoConfig(
    label: 'Pago',
    color: Color(0xFF10B981),
    bgColor: Color(0xFFD1FAE5),
    icon: Icons.credit_card,
  ),
  'PROMOCION': _TipoConfig(
    label: 'Promocion',
    color: Color(0xFFF59E0B),
    bgColor: Color(0xFFFEF3C7),
    icon: Icons.local_offer,
  ),
};

// ── Pantalla Principal ─────────────────────────────────────────
class RecordatoriosScreen extends StatefulWidget {
  const RecordatoriosScreen({Key? key}) : super(key: key);

  @override
  State<RecordatoriosScreen> createState() => _RecordatoriosScreenState();
}

class _RecordatoriosScreenState extends State<RecordatoriosScreen>
    with SingleTickerProviderStateMixin {
  final RecordatorioRepository _repo = RecordatorioRepository();
  final AuthRepository _authRepo = AuthRepository();

  late TabController _tabController;

  List<RecordatorioModel> _todos = [];
  List<RecordatorioModel> _proximos = [];
  bool _isLoading = true;
  String? _error;
  String _filtroTipo = '';
  String _storeName = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _inicializar();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _inicializar() async {
    final schema = await _authRepo.getSchemaName();
    setState(() => _storeName = schema ?? '');
    await _cargar();
  }

  Future<void> _cargar() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final todos = await _repo.getRecordatorios(
        tipo: _filtroTipo.isEmpty ? null : _filtroTipo,
      );
      final proximos = await _repo.getProximos();
      setState(() {
        _todos = todos;
        _proximos = proximos;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  // ── Pendientes / Completados ──────────────────────────────────
  List<RecordatorioModel> get _pendientes => _todos.where((r) => !r.completado).toList();
  List<RecordatorioModel> get _completados => _todos.where((r) => r.completado).toList();

  // ── Marcar completado ─────────────────────────────────────────
  Future<void> _marcarCompletado(RecordatorioModel rec) async {
    try {
      await _repo.marcarCompletado(rec.id);
      await _cargar();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Recordatorio marcado como completado'),
          backgroundColor: const Color(0xFF10B981),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
    } catch (e) {
      _mostrarError(e.toString());
    }
  }

  // ── Eliminar ──────────────────────────────────────────────────
  Future<void> _eliminar(RecordatorioModel rec) async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Eliminar Recordatorio'),
        content: Text('¿Eliminar "${rec.titulo}"? Esta acción no se puede deshacer.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Eliminar', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
    if (confirmar == true) {
      try {
        await _repo.eliminarRecordatorio(rec.id);
        await _cargar();
      } catch (e) {
        _mostrarError(e.toString());
      }
    }
  }

  void _mostrarError(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg.replaceAll('Exception: ', '')),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  // ── Bottom sheet: Crear / Editar ──────────────────────────────
  void _abrirFormulario({RecordatorioModel? editando}) {
    final tituloCtrl = TextEditingController(text: editando?.titulo ?? '');
    final descCtrl = TextEditingController(text: editando?.descripcion ?? '');
    String tipo = editando?.tipo ?? 'TAREA';
    DateTime? fecha = editando?.fechaRecordatorio;
    bool guardando = false;
    String errForm = '';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModal) => Container(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 24,
            left: 24, right: 24, top: 24,
          ),
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Handle
                Center(
                  child: Container(
                    width: 40, height: 4,
                    margin: const EdgeInsets.only(bottom: 20),
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                Row(
                  children: [
                    Icon(
                      editando != null ? Icons.edit_outlined : Icons.add_circle_outline,
                      size: 20,
                      color: const Color(0xFF6366F1),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      editando != null ? 'Editar Recordatorio' : 'Nuevo Recordatorio',
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                if (errForm.isNotEmpty) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFEE2E2),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Text(errForm, style: const TextStyle(color: Color(0xFFB91C1C), fontSize: 13)),
                  ),
                ],

                // Título
                _buildLabel('Título *'),
                TextField(
                  controller: tituloCtrl,
                  decoration: _inputDecoration('Ej: Pagar proveedor ABC'),
                ),
                const SizedBox(height: 14),

                // Descripción
                _buildLabel('Descripción (opcional)'),
                TextField(
                  controller: descCtrl,
                  maxLines: 2,
                  decoration: _inputDecoration('Detalles adicionales'),
                ),
                const SizedBox(height: 14),

                // Tipo
                _buildLabel('Tipo *'),
                DropdownButtonFormField<String>(
                  value: tipo,
                  decoration: _inputDecoration(''),
                  items: const [
                    DropdownMenuItem(value: 'TAREA',    child: Text('Tarea')),
                    DropdownMenuItem(value: 'PAGO',     child: Text('Pago')),
                    DropdownMenuItem(value: 'PROMOCION', child: Text('Promocion')),
                  ],
                  onChanged: (v) { if (v != null) setModal(() => tipo = v); },
                ),
                const SizedBox(height: 14),

                // Fecha y Hora
                _buildLabel('Fecha y Hora del Evento *'),
                InkWell(
                  onTap: () async {
                    final d = await showDatePicker(
                      context: ctx,
                      initialDate: fecha ?? DateTime.now(),
                      firstDate: DateTime(2020),
                      lastDate: DateTime(2030),
                    );
                    if (d == null) return;
                    final t = await showTimePicker(
                      context: ctx,
                      initialTime: TimeOfDay.fromDateTime(fecha ?? DateTime.now()),
                    );
                    if (t == null) return;
                    setModal(() {
                      fecha = DateTime(d.year, d.month, d.day, t.hour, t.minute);
                    });
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.calendar_today, size: 18, color: Color(0xFF6366F1)),
                        const SizedBox(width: 10),
                        Text(
                          fecha != null
                              ? '${fecha!.day.toString().padLeft(2, '0')}/${fecha!.month.toString().padLeft(2, '0')}/${fecha!.year}  ${fecha!.hour.toString().padLeft(2, '0')}:${fecha!.minute.toString().padLeft(2, '0')}'
                              : 'Seleccionar fecha y hora',
                          style: TextStyle(
                            color: fecha != null ? Colors.black87 : Colors.grey,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Botones
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => Navigator.pop(ctx),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        child: const Text('Cancelar'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: guardando
                            ? null
                            : () async {
                                if (tituloCtrl.text.trim().isEmpty) {
                                  setModal(() => errForm = 'El título es requerido.');
                                  return;
                                }
                                if (fecha == null) {
                                  setModal(() => errForm = 'La fecha es requerida.');
                                  return;
                                }
                                setModal(() => guardando = true);
                                try {
                                  final body = {
                                    'titulo': tituloCtrl.text.trim(),
                                    'descripcion': descCtrl.text.trim(),
                                    'tipo': tipo,
                                    'fecha_recordatorio': fecha!.toIso8601String(),
                                  };
                                  if (editando != null) {
                                    await _repo.actualizarRecordatorio(editando.id, body);
                                  } else {
                                    await _repo.crearRecordatorio(body);
                                  }
                                  if (!ctx.mounted) return;
                                  Navigator.pop(ctx);
                                  await _cargar();
                                } catch (e) {
                                  setModal(() {
                                    errForm = e.toString().replaceAll('Exception: ', '');
                                    guardando = false;
                                  });
                                }
                              },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF6366F1),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        child: guardando
                            ? const SizedBox(
                                width: 20, height: 20,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                              )
                            : Text(
                                editando != null ? 'Actualizar' : 'Crear Recordatorio',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                              ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLabel(String text) => Padding(
        padding: const EdgeInsets.only(bottom: 6),
        child: Text(text, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF374151))),
      );

  InputDecoration _inputDecoration(String hint) => InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.grey),
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF6366F1), width: 1.5),
        ),
      );

  // ── Tarjeta individual ────────────────────────────────────────
  Widget _buildCard(RecordatorioModel rec) {
    final cfg = _tipoConfig[rec.tipo] ?? _tipoConfig['TAREA']!;
    final ahora = DateTime.now();
    final vencido = !rec.completado && rec.fechaRecordatorio.isBefore(ahora);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: rec.completado ? const Color(0xFFF8FAFC) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: vencido ? Colors.red.shade200 : Colors.grey.shade200,
        ),
        boxShadow: rec.completado
            ? []
            : [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: IntrinsicHeight(
        child: Row(
          children: [
            // Acento lateral de color
            Container(
              width: 6,
              decoration: BoxDecoration(
                color: rec.completado ? Colors.grey.shade300 : cfg.color,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  bottomLeft: Radius.circular(16),
                ),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            rec.titulo,
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                              color: rec.completado ? Colors.grey : const Color(0xFF0F172A),
                              decoration: rec.completado ? TextDecoration.lineThrough : null,
                            ),
                          ),
                        ),
                        // Badge tipo
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: rec.completado ? Colors.grey.shade100 : cfg.bgColor,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(cfg.icon, size: 12, color: rec.completado ? Colors.grey : cfg.color),
                              const SizedBox(width: 4),
                              Text(
                                cfg.label,
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                  color: rec.completado ? Colors.grey : cfg.color,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    if (rec.descripcion.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        rec.descripcion,
                        style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    const SizedBox(height: 8),
                    // Fecha
                    Row(
                      children: [
                        Icon(
                          vencido ? Icons.warning_amber_rounded : Icons.schedule,
                          size: 13,
                          color: vencido ? Colors.red : Colors.grey,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          _formatFecha(rec.fechaRecordatorio),
                          style: TextStyle(
                            fontSize: 12,
                            color: vencido ? Colors.red : Colors.grey,
                            fontWeight: vencido ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                        if (vencido) ...[
                          const SizedBox(width: 4),
                          const Text('• Vencido', style: TextStyle(fontSize: 11, color: Colors.red, fontWeight: FontWeight.bold)),
                        ],
                      ],
                    ),
                    if (rec.pedidoId != null) ...[
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Icon(Icons.link, size: 13, color: Color(0xFF6366F1)),
                          const SizedBox(width: 4),
                          Text('Pedido #${rec.pedidoId}', style: const TextStyle(fontSize: 12, color: Color(0xFF6366F1), fontWeight: FontWeight.w600)),
                        ],
                      ),
                    ],
                    // Acciones
                    if (!rec.completado) ...[
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          _buildActionChip(
                            label: 'Completar',
                            icon: Icons.check_circle_outline,
                            color: const Color(0xFF10B981),
                            onTap: () => _marcarCompletado(rec),
                          ),
                          const SizedBox(width: 8),
                          _buildActionChip(
                            label: 'Editar',
                            icon: Icons.edit_outlined,
                            color: const Color(0xFF6366F1),
                            onTap: () => _abrirFormulario(editando: rec),
                          ),
                          const SizedBox(width: 8),
                          _buildActionChip(
                            label: 'Eliminar',
                            icon: Icons.delete_outline,
                            color: Colors.red,
                            onTap: () => _eliminar(rec),
                          ),
                        ],
                      ),
                    ] else ...[
                      const SizedBox(height: 10),
                      Row(children: [
                        _buildActionChip(
                          label: 'Eliminar',
                          icon: Icons.delete_outline,
                          color: Colors.red,
                          onTap: () => _eliminar(rec),
                        ),
                      ]),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionChip({
    required String label,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          border: Border.all(color: color.withOpacity(0.4)),
          borderRadius: BorderRadius.circular(8),
          color: color.withOpacity(0.05),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 12, color: color),
            const SizedBox(width: 4),
            Text(label, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }

  String _formatFecha(DateTime dt) {
    return '${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year}  ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }

  // ── Build principal ───────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return AppDashboardLayout(
      brandName: 'MiQhatu',
      tenantValue: _storeName,
      userName: '',
      sidebarItems: [
        AppSidebarItem(icon: Icons.dashboard, label: 'Panel',
            onTap: () => Navigator.pushReplacementNamed(context, '/dashboard')),
        AppSidebarItem(icon: Icons.inventory_2, label: 'Productos',
            onTap: () => Navigator.pushReplacementNamed(context, '/productos')),
        AppSidebarItem(icon: Icons.shopping_cart, label: 'Ventas',
            onTap: () => Navigator.pushReplacementNamed(context, '/ventas')),
        AppSidebarItem(icon: Icons.people, label: 'Clientes',
            onTap: () => Navigator.pushReplacementNamed(context, '/clientes')),
        AppSidebarItem(icon: Icons.bar_chart, label: 'Reportes',
            onTap: () => Navigator.pushReplacementNamed(context, '/reportes')),
        AppSidebarItem(
          icon: Icons.alarm,
          label: 'Recordatorios',
          isActive: true,
          onTap: () => Navigator.pushReplacementNamed(context, '/recordatorios'),
        ),
        AppSidebarItem(icon: Icons.settings, label: 'Configuración',
            onTap: () => Navigator.pushReplacementNamed(context, '/configuracion')),
        AppSidebarItem(icon: Icons.logout, label: 'Salir', isLogout: true,
            onTap: () => Navigator.pushReplacementNamed(context, '/login')),
      ],
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Título y botón
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.alarm, size: 22, color: Color(0xFF6366F1)),
                      const SizedBox(width: 8),
                      Text('Recordatorios', style: AppTextStyles.h1.copyWith(fontSize: 22)),
                    ],
                  ),
                  Text('Gestiona tareas, pagos y promociones', style: AppTextStyles.subtitle),
                ],
              ),
              ElevatedButton.icon(
                onPressed: () => _abrirFormulario(),
                icon: const Icon(Icons.add, size: 18, color: Colors.white),
                label: const Text('Nuevo', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6366F1),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Banner próximos
          if (_proximos.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: const Color(0xFFFEF3C7),
                border: Border.all(color: const Color(0xFFF59E0B)),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_rounded, color: Color(0xFFD97706), size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${_proximos.length} recordatorio${_proximos.length > 1 ? 's' : ''} pendiente${_proximos.length > 1 ? 's' : ''} en los próximos 7 días',
                      style: const TextStyle(fontSize: 13, color: Color(0xFF92400E), fontWeight: FontWeight.w500),
                    ),
                  ),
                ],
              ),
            ),

          // Filtros por tipo
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                for (final f in [
                  {'value': '', 'label': 'Todos'},
                  {'value': 'TAREA',    'label': 'Tareas'},
                  {'value': 'PAGO',     'label': 'Pagos'},
                  {'value': 'PROMOCION', 'label': 'Promociones'},
                ])
                  Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: FilterChip(
                      label: Text(f['label']!),
                      selected: _filtroTipo == f['value'],
                      onSelected: (_) {
                        setState(() => _filtroTipo = f['value']!);
                        _cargar();
                      },
                      selectedColor: const Color(0xFF6366F1).withOpacity(0.15),
                      checkmarkColor: const Color(0xFF6366F1),
                      labelStyle: TextStyle(
                        color: _filtroTipo == f['value']
                            ? const Color(0xFF6366F1)
                            : Colors.grey,
                        fontWeight: FontWeight.w600,
                        fontSize: 12,
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // Tabs
          TabBar(
            controller: _tabController,
            labelColor: const Color(0xFF6366F1),
            unselectedLabelColor: Colors.grey,
            indicatorColor: const Color(0xFF6366F1),
            labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
            tabs: [
              Tab(text: 'Pendientes (${_pendientes.length})'),
              Tab(text: 'Completados (${_completados.length})'),
            ],
          ),
          const SizedBox(height: 16),

          // Contenido
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF6366F1)))
                : _error != null
                    ? Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
                    : TabBarView(
                        controller: _tabController,
                        children: [
                          // Pendientes
                          _pendientes.isEmpty
                              ? const Center(
                                  child: Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(Icons.alarm_off, size: 48, color: Colors.grey),
                                      SizedBox(height: 12),
                                      Text('No hay recordatorios pendientes',
                                          style: TextStyle(color: Colors.grey, fontSize: 15)),
                                      SizedBox(height: 4),
                                      Text('Toca el botón + para crear uno',
                                          style: TextStyle(color: Colors.grey, fontSize: 13)),
                                    ],
                                  ),
                                )
                              : RefreshIndicator(
                                  onRefresh: _cargar,
                                  color: const Color(0xFF6366F1),
                                  child: ListView(
                                    children: _pendientes.map(_buildCard).toList(),
                                  ),
                                ),
                          // Completados
                          _completados.isEmpty
                              ? const Center(
                                  child: Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(Icons.check_circle_outline, size: 48, color: Colors.grey),
                                      SizedBox(height: 12),
                                      Text('No hay recordatorios completados',
                                          style: TextStyle(color: Colors.grey, fontSize: 15)),
                                    ],
                                  ),
                                )
                              : ListView(
                                  children: _completados.map(_buildCard).toList(),
                                ),
                        ],
                      ),
          ),
        ],
      ),
    );
  }
}
