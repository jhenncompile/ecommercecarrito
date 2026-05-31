import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../core/theme/app_colors.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/cards/app_table_card.dart';
import '../repositories/report_repository.dart';

class ReporteBasicoTab extends StatefulWidget {
  const ReporteBasicoTab({super.key});

  @override
  State<ReporteBasicoTab> createState() => _ReporteBasicoTabState();
}

class _ReporteBasicoTabState extends State<ReporteBasicoTab> {
  final ReportRepository _reportRepository = ReportRepository();
  bool _isLoading = false;
  String _selectedReportType = 'ventas_mensuales';
  List<dynamic>? _resultData;
  String? _error;

  final Map<String, String> _reportTypes = {
    'ventas_mensuales': 'Ventas Mensuales',
    'ventas_anuales': 'Ventas Anuales',
    'top_productos': 'Top Productos Más Vendidos',
    'top_categorias': 'Top Categorías Más Vendidas',
    'nuevos_clientes': 'Nuevos Clientes por Mes',
    'nuevos_clientes_anual': 'Nuevos Clientes por Año',
  };

  Future<void> _fetchReport() async {
    setState(() {
      _isLoading = true;
      _error = null;
      _resultData = null;
    });

    try {
      final data = await _reportRepository.getReporteEstatico(_selectedReportType);
      setState(() {
        _resultData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Error al cargar reporte: $e';
        _isLoading = false;
      });
    }
  }

  String _formatHeader(String key) {
    return key.replaceFirst(key[0], key[0].toUpperCase()).replaceAll('_', ' ');
  }

  String _formatValue(String key, dynamic value) {
    if (value == null) return '-';
    String valStr = value.toString();
    if (key == 'mes' || key == 'fecha' || key == 'periodo' || key == 'año' || key == 'anio') {
      try {
        // Extraer la parte de la fecha antes de la T (ej. 2026-05-01T00:00:00)
        String datePart = valStr.split('T')[0];
        final parts = datePart.split('-');
        
        if (_selectedReportType.contains('anual') || key == 'año' || key == 'anio') {
          return parts[0]; // Retorna solo el año
        } else {
          // Es mensual o diario
          final months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
          if (parts.length >= 2) {
            int m = int.tryParse(parts[1]) ?? 1;
            return '${months[m-1]} ${parts[0]}';
          }
        }
      } catch (e) {
        // Ignorar si no es una fecha parseable
      }
    }
    return valStr;
  }

  Widget _buildChart(List<dynamic> resultadosFull) {
    if (resultadosFull.isEmpty) return const SizedBox();
    
    // Simplificar el gráfico a los últimos 4 periodos
    List<dynamic> resultados = resultadosFull.length > 4 
        ? resultadosFull.sublist(resultadosFull.length - 4) 
        : resultadosFull;

    // Identificar clave X (label) y clave Y (valor)
    final firstRow = resultados[0] as Map<String, dynamic>;
    String xKey = '';
    String yKey = '';

    for (var key in firstRow.keys) {
      if (key == 'mes' || key == 'año' || key == 'anio' || key == 'nombre' || key == 'fecha' || key == 'periodo') {
        xKey = key;
      } else if (yKey.isEmpty && (firstRow[key] is num || double.tryParse(firstRow[key]?.toString() ?? '') != null)) {
        yKey = key;
      }
    }

    if (xKey.isEmpty) xKey = firstRow.keys.first;
    if (yKey.isEmpty && firstRow.keys.length > 1) yKey = firstRow.keys.last;

    if (yKey.isEmpty) return const Center(child: Text('Datos no graficables'));

    List<BarChartGroupData> barGroups = [];
    double maxY = 0;

    for (int i = 0; i < resultados.length; i++) {
      final row = resultados[i];
      double yVal = double.tryParse(row[yKey]?.toString() ?? '0') ?? 0;
      if (yVal > maxY) maxY = yVal;

      barGroups.add(
        BarChartGroupData(
          x: i,
          barRods: [
            BarChartRodData(
              toY: yVal,
              color: AppColors.accentTeal,
              width: 16,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
            ),
          ],
        ),
      );
    }

    maxY = maxY * 1.2;
    if (maxY == 0) maxY = 10;

    return BarChart(
      BarChartData(
        gridData: FlGridData(show: false),
        borderData: FlBorderData(show: false),
        titlesData: FlTitlesData(
          show: true,
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                int index = value.toInt();
                if (index >= 0 && index < resultados.length) {
                  final row = resultados[index] as Map<String, dynamic>;
                  String label = _formatValue(xKey, row[xKey] ?? '');
                  if (label.length > 8) label = label.substring(0, 8) + '..';
                  return Padding(
                    padding: const EdgeInsets.only(top: 5),
                    child: Text(label, style: const TextStyle(fontSize: 9, color: AppColors.textMuted)),
                  );
                }
                return const SizedBox();
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              getTitlesWidget: (value, meta) {
                if (value == maxY) return const SizedBox();
                return Text(value.toInt().toString(), style: const TextStyle(fontSize: 10, color: AppColors.textMuted));
              },
            ),
          ),
        ),
        minY: 0,
        maxY: maxY,
        barGroups: barGroups,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
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
              const Text(
                'Seleccione el tipo de reporte estático a generar:',
                style: TextStyle(color: AppColors.textMuted, fontSize: 14),
              ),
              const SizedBox(height: 15),
              Row(
                children: [
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 15),
                      decoration: BoxDecoration(
                        border: Border.all(color: AppColors.border),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: _selectedReportType,
                          isExpanded: true,
                          items: _reportTypes.entries.map((entry) {
                            return DropdownMenuItem<String>(
                              value: entry.key,
                              child: Text(entry.value, style: const TextStyle(fontSize: 14)),
                            );
                          }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              setState(() {
                                _selectedReportType = val;
                                _resultData = null; // resetear resultados
                              });
                            }
                          },
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 15),
                  AppButton.add(
                    label: _isLoading ? 'Cargando...' : 'Generar',
                    icon: Icons.play_arrow,
                    onPressed: _isLoading ? null : _fetchReport,
                  ),
                ],
              ),
            ],
          ),
        ),
        
        if (_error != null) ...[
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(15),
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

        if (_isLoading)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 40),
            child: Center(child: CircularProgressIndicator(color: AppColors.accentTeal)),
          ),

        if (_resultData != null && !_isLoading) ...[
          const SizedBox(height: 30),
          if (_resultData!.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(40),
                child: Text('No hay datos para este reporte.', style: TextStyle(color: AppColors.textMuted)),
              ),
            )
          else ...[
            // Gráfico
            Container(
              height: 250,
              padding: const EdgeInsets.all(15),
              margin: const EdgeInsets.only(bottom: 20),
              decoration: BoxDecoration(
                color: AppColors.bgCard,
                borderRadius: BorderRadius.circular(15),
                border: Border.all(color: AppColors.border),
              ),
              child: _buildChart(_resultData!),
            ),
            
            // Tabla
            AppTableCard(
              title: _reportTypes[_selectedReportType] ?? 'Reporte',
              columns: (_resultData![0] as Map<String, dynamic>)
                  .keys
                  .map((k) => _formatHeader(k))
                  .toList(),
              rows: _resultData!.map<List<Widget>>((row) {
                final map = row as Map<String, dynamic>;
                return map.entries.map<Widget>((entry) => Text(_formatValue(entry.key, entry.value))).toList();
              }).toList(),
            ),
          ],
        ],
      ],
    );
  }
}
