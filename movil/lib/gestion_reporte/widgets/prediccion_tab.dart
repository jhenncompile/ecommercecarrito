import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../core/theme/app_colors.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/cards/app_table_card.dart';
import '../repositories/report_repository.dart';

class PrediccionTab extends StatefulWidget {
  final String endpoint; // '', 'productos', 'categorias'
  final String title;

  const PrediccionTab({
    super.key,
    required this.endpoint,
    required this.title,
  });

  @override
  State<PrediccionTab> createState() => _PrediccionTabState();
}

class _PrediccionTabState extends State<PrediccionTab> {
  final ReportRepository _reportRepository = ReportRepository();
  bool _isLoading = false;
  bool _isUpgrading = false;
  
  String _granularidad = 'mes';
  String _tipoPrediccion = 'ventas_totales';
  int _pasos = 3;

  Map<String, dynamic>? _resultData;
  String? _error;
  
  List<dynamic> _opciones = [];
  int? _selectedOpcionId;

  @override
  void initState() {
    super.initState();
    if (widget.endpoint.isNotEmpty) {
      _loadOpciones();
    }
  }

  Future<void> _loadOpciones() async {
    try {
      final opciones = await _reportRepository.getPrediccionOpciones(widget.endpoint);
      if (mounted) {
        setState(() {
          _opciones = opciones;
          if (opciones.isNotEmpty) {
            _selectedOpcionId = opciones[0]['id'];
          }
        });
      }
    } catch (e) {
      if (e.toString().contains('PLAN_REQUIRED')) {
        if (mounted) {
          setState(() {
            _error = 'PLAN_REQUIRED';
          });
        }
      }
    }
  }

  Future<void> _fetchPrediccion() async {
    setState(() {
      _isLoading = true;
      _error = null;
      _resultData = null;
    });

    try {
      int meses = _pasos;
      if (_granularidad == 'dia') meses = (_pasos / 30).ceil();
      else if (_granularidad == 'semana') meses = (_pasos / 4).ceil();
      else if (_granularidad == 'anio') meses = _pasos * 12;

      final params = {
        'granularidad': _granularidad,
        'prediccion_meses': meses.toString(),
      };
      
      if (widget.endpoint == '') {
        params['tipo'] = _tipoPrediccion;
      } else if (widget.endpoint == 'productos') {
        params['tipo'] = 'por_producto';
        if (_selectedOpcionId != null) params['producto_id'] = _selectedOpcionId!.toString();
      } else if (widget.endpoint == 'categorias') {
        params['tipo'] = 'por_categoria';
        if (_selectedOpcionId != null) params['categoria_id'] = _selectedOpcionId!.toString();
      }

      final data = await _reportRepository.getPrediccion(widget.endpoint, params);
      setState(() {
        _resultData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Error al generar predicción: $e';
        _isLoading = false;
      });
    }
  }

  String _formatHeader(String key) {
    return key.replaceFirst(key[0], key[0].toUpperCase()).replaceAll('_', ' ');
  }

  String _formatValue(String key, dynamic value) {
    if (value == null) return '-';
    if (key == 'es_prediccion') return value.toString();
    
    String valStr = value.toString();
    if (key == 'periodo' || key == 'fecha') {
      try {
        String datePart = valStr.split('T')[0];
        final parts = datePart.split('-');
        
        if (_granularidad == 'anio') {
          return parts[0];
        } else if (_granularidad == 'mes' && parts.length >= 2) {
          final months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
          int m = int.tryParse(parts[1]) ?? 1;
          return '${months[m-1]} ${parts[0]}';
        } else if (parts.length >= 3) {
          final months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
          int m = int.tryParse(parts[1]) ?? 1;
          return '${parts[2]} ${months[m-1]} ${parts[0]}';
        }
      } catch (e) {
        // Ignorar errores de parseo
      }
    }
    return valStr;
  }

  @override
  Widget build(BuildContext context) {
    final metricas = _resultData?['metricas'];
    
    final historicoRaw = _resultData?['historico'] as List<dynamic>? ?? [];
    final prediccionesRaw = _resultData?['predicciones'] as List<dynamic>? ?? [];

    List<dynamic> resultados = [];
    if (_resultData != null) {
      for (var item in historicoRaw) {
        resultados.add({
          'periodo': item['periodo'],
          'cantidad': item['cantidad'],
          'es_prediccion': false,
        });
      }
      for (var item in prediccionesRaw) {
        resultados.add({
          'periodo': item['periodo'],
          'cantidad': item['cantidad_estimada'] ?? item['cantidad'],
          'es_prediccion': true,
        });
      }
    }

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
              Text(
                'Parámetros para predicción de ${widget.title}',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppColors.primaryDark),
              ),
              const SizedBox(height: 15),
              
              Wrap(
                spacing: 15,
                runSpacing: 15,
                children: [
                  // Selección de Producto/Categoría
                  if (widget.endpoint.isNotEmpty)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(widget.endpoint == 'productos' ? 'Producto' : 'Categoría', style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
                        const SizedBox(height: 5),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10),
                          decoration: BoxDecoration(border: Border.all(color: AppColors.border), borderRadius: BorderRadius.circular(8)),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<int>(
                              value: _selectedOpcionId,
                              hint: Text('Seleccione...'),
                              items: _opciones.map((op) {
                                return DropdownMenuItem<int>(
                                  value: op['id'],
                                  child: Text(op['nombre'] ?? op.toString()),
                                );
                              }).toList(),
                              onChanged: (val) {
                                if (val != null) setState(() => _selectedOpcionId = val);
                              },
                            ),
                          ),
                        ),
                      ],
                    ),

                  // Granularidad
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Granularidad', style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                      const SizedBox(height: 5),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        decoration: BoxDecoration(border: Border.all(color: AppColors.border), borderRadius: BorderRadius.circular(8)),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            value: _granularidad,
                            items: const [
                              DropdownMenuItem(value: 'dia', child: Text('Diaria')),
                              DropdownMenuItem(value: 'semana', child: Text('Semanal')),
                              DropdownMenuItem(value: 'mes', child: Text('Mensual')),
                              DropdownMenuItem(value: 'anio', child: Text('Anual')),
                            ],
                            onChanged: (val) {
                              if (val != null) {
                                setState(() {
                                  _granularidad = val;
                                  List<int> options;
                                  switch (val) {
                                    case 'dia': options = [30, 60, 90, 120]; break;
                                    case 'semana': options = [4, 8, 12, 24]; break;
                                    case 'anio': options = [1, 2, 3, 5]; break;
                                    default: options = [3, 6, 9, 12]; break;
                                  }
                                  if (!options.contains(_pasos)) {
                                    _pasos = options.first;
                                  }
                                });
                              }
                            },
                          ),
                        ),
                      ),
                    ],
                  ),

                  // Pasos
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Períodos a predecir', style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                      const SizedBox(height: 5),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        decoration: BoxDecoration(border: Border.all(color: AppColors.border), borderRadius: BorderRadius.circular(8)),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<int>(
                            value: _pasos,
                            items: (() {
                              switch (_granularidad) {
                                case 'dia': return [30, 60, 90, 120];
                                case 'semana': return [4, 8, 12, 24];
                                case 'anio': return [1, 2, 3, 5];
                                default: return [3, 6, 9, 12];
                              }
                            }()).map((p) {
                              String label = '';
                              switch (_granularidad) {
                                case 'dia': label = 'días'; break;
                                case 'semana': label = 'semanas'; break;
                                case 'mes': label = 'meses'; break;
                                case 'anio': label = 'años'; break;
                              }
                              return DropdownMenuItem(value: p, child: Text('$p $label'));
                            }).toList(),
                            onChanged: (val) {
                              if (val != null) setState(() => _pasos = val);
                            },
                          ),
                        ),
                      ),
                    ],
                  ),

                  // Tipo (Solo para Ventas)
                  if (widget.endpoint == '')
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Métrica', style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                        const SizedBox(height: 5),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10),
                          decoration: BoxDecoration(border: Border.all(color: AppColors.border), borderRadius: BorderRadius.circular(8)),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<String>(
                              value: _tipoPrediccion,
                              items: const [
                                DropdownMenuItem(value: 'ventas_totales', child: Text('Ventas Totales (\$)')),
                                DropdownMenuItem(value: 'ventas_cantidad', child: Text('Cantidad de Pedidos')),
                              ],
                              onChanged: (val) {
                                if (val != null) setState(() => _tipoPrediccion = val);
                              },
                            ),
                          ),
                        ),
                      ],
                    ),
                ],
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: AppButton.add(
                  label: _isLoading ? 'Analizando...' : 'Generar Predicción',
                  icon: Icons.online_prediction,
                  onPressed: _isLoading ? null : _fetchPrediccion,
                ),
              ),
            ],
          ),
        ),
        
        if (_error != null) ...[
          const SizedBox(height: 20),
          if (_error!.contains('PLAN_REQUIRED'))
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFFF59E0B), Color(0xFFD97706)]),
                borderRadius: BorderRadius.circular(15),
                boxShadow: [BoxShadow(color: Color(0xFFF59E0B).withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 4))],
              ),
              child: Column(
                children: [
                  const Icon(Icons.diamond, color: Colors.white, size: 48),
                  const SizedBox(height: 10),
                  const Text('Función Premium', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 5),
                  const Text('Mejora tu plan para acceder a predicciones avanzadas con IA.', textAlign: TextAlign.center, style: TextStyle(color: Colors.white)),
                  const SizedBox(height: 15),
                  _isUpgrading 
                    ? const CircularProgressIndicator(color: Colors.white)
                    : ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white,
                          foregroundColor: const Color(0xFFD97706),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        onPressed: () async {
                          setState(() => _isUpgrading = true);
                          try {
                            await _reportRepository.upgradePlan();
                            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Plan mejorado con éxito. Refrescando...')));
                            setState(() {
                              _error = null;
                            });
                            // Reintentar cargar
                            _loadOpciones();
                            _fetchPrediccion();
                          } catch (e) {
                            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
                          } finally {
                            setState(() => _isUpgrading = false);
                          }
                        },
                        child: const Text('Mejorar Plan Ahora', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                ],
              ),
            )
          else
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
          
          // Métricas
          if (metricas != null)
            Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: AppColors.bgCard,
                      borderRadius: BorderRadius.circular(15),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Column(
                      children: [
                        const Text('Promedio Histórico', style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                        const SizedBox(height: 5),
                        Text(
                          '${metricas['promedio_por_periodo'] ?? 0}',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: AppColors.primaryDark),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 15),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(colors: [AppColors.accentTeal, Color(0xFF059669)]),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: Column(
                      children: [
                        const Text('Datos Analizados', style: TextStyle(color: Colors.white70, fontSize: 12)),
                        const SizedBox(height: 5),
                        Text(
                          '${metricas['datos_usados'] ?? 0} per.',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: Colors.white),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          
          const SizedBox(height: 20),
          
          // Gráfico
          if (resultados.isNotEmpty)
            Container(
              height: 250,
              padding: const EdgeInsets.all(15),
              margin: const EdgeInsets.only(bottom: 20),
              decoration: BoxDecoration(
                color: AppColors.bgCard,
                borderRadius: BorderRadius.circular(15),
                border: Border.all(color: AppColors.border),
              ),
              child: _buildChart(resultados),
            ),
            
          // Tabla
          if (resultados.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(40),
                child: Text('No hay datos de predicción suficientes.', style: TextStyle(color: AppColors.textMuted)),
              ),
            )
          else
            AppTableCard(
              title: 'Proyección: ${widget.title}',
              // Filtrar la columna 'es_prediccion' en el header
              columns: (resultados[0] as Map<String, dynamic>)
                  .keys
                  .where((k) => k != 'es_prediccion')
                  .map((k) => _formatHeader(k))
                  .toList(),
              rows: resultados.reversed.map<List<Widget>>((row) {
                final map = row as Map<String, dynamic>;
                final isPrediction = map['es_prediccion'] == true;
                
                // Mapear solo las keys que no sean es_prediccion
                return map.entries
                    .where((entry) => entry.key != 'es_prediccion')
                    .map<Widget>((entry) {
                  return Text(
                    _formatValue(entry.key, entry.value),
                    style: TextStyle(
                      color: isPrediction ? AppColors.accentTeal : AppColors.textPrimary,
                      fontWeight: isPrediction ? FontWeight.bold : FontWeight.normal,
                    ),
                  );
                }).toList();
              }).toList(),
            ),
        ],
      ],
    );
  }

  Widget _buildChart(List<dynamic> resultados) {
    if (resultados.isEmpty) return const SizedBox();

    const String yKey = 'cantidad';
    double maxY = 0;
    List<FlSpot> historicoSpots = [];
    List<FlSpot> prediccionSpots = [];

    for (int i = 0; i < resultados.length; i++) {
      final row = resultados[i] as Map<String, dynamic>;
      double yVal = double.tryParse(row[yKey]?.toString() ?? '0') ?? 0;
      if (yVal > maxY) maxY = yVal;

      if (row['es_prediccion'] == true) {
        if (prediccionSpots.isEmpty && i > 0) {
          final prevRow = resultados[i - 1] as Map<String, dynamic>;
          double prevY = double.tryParse(prevRow[yKey]?.toString() ?? '0') ?? 0;
          prediccionSpots.add(FlSpot((i - 1).toDouble(), prevY));
        }
        prediccionSpots.add(FlSpot(i.toDouble(), yVal));
      } else {
        historicoSpots.add(FlSpot(i.toDouble(), yVal));
      }
    }

    // Add 20% top margin
    maxY = maxY * 1.2;
    if (maxY == 0) maxY = 10;

    return LineChart(
      LineChartData(
        gridData: FlGridData(show: true, drawVerticalLine: false),
        borderData: FlBorderData(show: false),
        titlesData: FlTitlesData(
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                int index = value.toInt();
                if (index >= 0 && index < resultados.length) {
                  String label = resultados[index]['fecha'] ?? resultados[index]['periodo'] ?? '';
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
                return Text(value.toInt().toString(), style: const TextStyle(fontSize: 10, color: AppColors.textMuted));
              },
            ),
          ),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        minY: 0,
        maxY: maxY,
        lineBarsData: [
          // Historical line
          LineChartBarData(
            spots: historicoSpots,
            isCurved: true,
            color: AppColors.primaryDark,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              color: AppColors.primaryDark.withOpacity(0.1),
            ),
          ),
          // Prediction line
          LineChartBarData(
            spots: prediccionSpots,
            isCurved: true,
            color: AppColors.accentTeal,
            barWidth: 3,
            dashArray: [5, 5],
            isStrokeCapRound: true,
            dotData: FlDotData(show: true),
            belowBarData: BarAreaData(
              show: true,
              color: AppColors.accentTeal.withOpacity(0.2),
            ),
          ),
        ],
      ),
    );
  }
}
