import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/widgets/cards/app_table_card.dart';
import '../repositories/report_repository.dart';

class ReporteDinamicoTab extends StatefulWidget {
  const ReporteDinamicoTab({super.key});

  @override
  State<ReporteDinamicoTab> createState() => _ReporteDinamicoTabState();
}

class _ReporteDinamicoTabState extends State<ReporteDinamicoTab> {
  final ReportRepository _reportRepository = ReportRepository();
  bool _isLoadingConfigs = true;
  bool _isExecuting = false;
  List<dynamic> _configs = [];
  Map<String, dynamic>? _selectedConfig;
  List<dynamic>? _resultData;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadConfigs();
  }

  Future<void> _loadConfigs() async {
    setState(() {
      _isLoadingConfigs = true;
      _error = null;
    });

    try {
      final data = await _reportRepository.getReportesDinamicosGuardados();
      setState(() {
        _configs = data;
        _isLoadingConfigs = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Error al cargar configuraciones: $e';
        _isLoadingConfigs = false;
      });
    }
  }

  Future<void> _ejecutarConfiguracion(Map<String, dynamic> config) async {
    setState(() {
      _selectedConfig = config;
      _isExecuting = true;
      _error = null;
      _resultData = null;
    });

    try {
      // El backend en /api/reportes/builder/ recibe un objeto JSON similar a la estructura de "configuracion"
      final data = await _reportRepository.ejecutarReporteDinamico(config['configuracion']);
      setState(() {
        _resultData = data;
        _isExecuting = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Error al ejecutar: $e';
        _isExecuting = false;
      });
    }
  }

  String _formatHeader(String key) {
    return key.replaceFirst(key[0], key[0].toUpperCase()).replaceAll('_', ' ');
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (_error != null) ...[
          Container(
            padding: const EdgeInsets.all(15),
            margin: const EdgeInsets.only(bottom: 20),
            decoration: BoxDecoration(color: AppColors.danger.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
            child: Row(
              children: [
                const Icon(Icons.error_outline, color: AppColors.danger),
                const SizedBox(width: 10),
                Expanded(child: Text(_error!, style: const TextStyle(color: AppColors.danger))),
              ],
            ),
          ),
        ],

        if (_isLoadingConfigs)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 40),
            child: Center(child: CircularProgressIndicator(color: AppColors.accentTeal)),
          )
        else ...[
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.bgCard,
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Expanded(
                      child: Text(
                        'Reportes Personalizados Guardados',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppColors.primaryDark),
                        overflow: TextOverflow.visible,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.refresh, color: AppColors.accentTeal),
                      onPressed: _loadConfigs,
                      tooltip: 'Actualizar',
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                if (_configs.isEmpty)
                  const Text('No hay reportes dinámicos guardados. Crea uno desde la versión web.', style: TextStyle(color: AppColors.textMuted))
                else
                  ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _configs.length,
                    separatorBuilder: (context, index) => const Divider(),
                    itemBuilder: (context, index) {
                      final conf = _configs[index];
                      return ListTile(
                        leading: const Icon(Icons.bar_chart, color: AppColors.accentTeal),
                        title: Text(conf['nombre'] ?? 'Sin nombre', style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text(conf['descripcion'] ?? 'Sin descripción'),
                        trailing: const Icon(Icons.play_arrow, color: AppColors.accentTeal),
                        onTap: _isExecuting ? null : () => _ejecutarConfiguracion(conf),
                      );
                    },
                  ),
              ],
            ),
          ),
          
          if (_isExecuting)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 40),
              child: Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(color: AppColors.accentTeal),
                    SizedBox(height: 10),
                    Text('Generando reporte dinámico...', style: TextStyle(color: AppColors.textMuted)),
                  ],
                ),
              ),
            ),

          if (_resultData != null && !_isExecuting) ...[
            const SizedBox(height: 30),
            if (_resultData!.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(40),
                  child: Text('El reporte no arrojó resultados.', style: TextStyle(color: AppColors.textMuted)),
                ),
              )
            else
              AppTableCard(
                title: _selectedConfig?['nombre'] ?? 'Resultados',
                columns: (_resultData![0] as Map<String, dynamic>)
                    .keys
                    .map((k) => _formatHeader(k))
                    .toList(),
                rows: _resultData!.map<List<Widget>>((row) {
                  final map = row as Map<String, dynamic>;
                  return map.values.map<Widget>((v) => Text(v?.toString() ?? '-')).toList();
                }).toList(),
              ),
          ],
        ],
      ],
    );
  }
}
