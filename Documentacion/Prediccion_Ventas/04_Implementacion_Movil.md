# Datos de Implementación - MÓVIL (Flutter)

## 📁 Estructura de Carpetas

```
movil/lib/
├── features/
│   ├── predicciones/  # [NUEVO] Módulo de predicciones
│   │   ├── data/
│   │   │   ├── datasources/
│   │   │   │   └── prediction_remote_datasource.dart
│   │   │   ├── models/
│   │   │   │   ├── prediction_model.dart
│   │   │   │   ├── forecast_request.dart
│   │   │   │   └── forecast_response.dart
│   │   │   └── repositories/
│   │   │       └── prediction_repository.dart
│   │   │
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── prediccion.dart
│   │   │   ├── repositories/
│   │   │   │   └── prediction_repository_abstract.dart
│   │   │   └── usecases/
│   │   │       ├── generar_prediccion.dart
│   │   │       ├── exportar_excel.dart
│   │   │       └── obtener_productos.dart
│   │   │
│   │   └── presentation/
│   │       ├── bloc/
│   │       │   ├── prediction_bloc.dart
│   │       │   ├── prediction_event.dart
│   │       │   └── prediction_state.dart
│   │       │
│   │       ├── pages/
│   │       │   └── predictions_page.dart
│   │       │
│   │       └── widgets/
│   │           ├── prediction_chart.dart
│   │           ├── prediction_table.dart
│   │           ├── filter_sheet.dart
│   │           ├── export_buttons.dart
│   │           └── empty_state.dart
│
└── core/
    └── services/
        └── file_service.dart  # Descargas de archivos
```

---

## 📦 MODELOS: prediction_model.dart

```dart
class Prediccion {
  final String periodo;
  final double? valorHistorico;
  final double valorPredicho;
  final double icInferior;
  final double icSuperior;
  final double confianza;
  final double? variacion;

  Prediccion({
    required this.periodo,
    this.valorHistorico,
    required this.valorPredicho,
    required this.icInferior,
    required this.icSuperior,
    required this.confianza,
    this.variacion,
  });

  factory Prediccion.fromJson(Map<String, dynamic> json) {
    return Prediccion(
      periodo: json['periodo'] as String,
      valorHistorico: json['valor_historico'] as double?,
      valorPredicho: (json['valor_predicho'] as num).toDouble(),
      icInferior: (json['ic_inferior'] as num).toDouble(),
      icSuperior: (json['ic_superior'] as num).toDouble(),
      confianza: (json['confianza'] as num).toDouble(),
      variacion: json['variacion'] as double?,
    );
  }

  Map<String, dynamic> toJson() => {
    'periodo': periodo,
    'valor_historico': valorHistorico,
    'valor_predicho': valorPredicho,
    'ic_inferior': icInferior,
    'ic_superior': icSuperior,
    'confianza': confianza,
    'variacion': variacion,
  };
}

class ForecastResponse {
  final List<Prediccion> predicciones;
  final List<Prediccion> historico;
  final Map<String, dynamic> metricas;
  final double confianza;

  ForecastResponse({
    required this.predicciones,
    required this.historico,
    required this.metricas,
    required this.confianza,
  });

  factory ForecastResponse.fromJson(Map<String, dynamic> json) {
    return ForecastResponse(
      predicciones: List<Prediccion>.from(
        (json['predicciones'] as List).map((p) => Prediccion.fromJson(p as Map<String, dynamic>))
      ),
      historico: List<Prediccion>.from(
        (json['historico'] as List? ?? []).map((h) => Prediccion.fromJson(h as Map<String, dynamic>))
      ),
      metricas: json['metricas'] as Map<String, dynamic>,
      confianza: (json['confianza'] as num).toDouble(),
    );
  }
}

class ForecastRequest {
  final int dataHistoricaMeses;
  final int prediccionMeses;
  final String granularidad; // dia, semana, mes, año
  final String tipo; // ventas_totales, por_producto, por_categoria
  final int? productoId;
  final int? categoriaId;

  ForecastRequest({
    required this.dataHistoricaMeses,
    required this.prediccionMeses,
    required this.granularidad,
    required this.tipo,
    this.productoId,
    this.categoriaId,
  });

  Map<String, dynamic> toJson() => {
    'data_historica_meses': dataHistoricaMeses,
    'prediccion_meses': prediccionMeses,
    'granularidad': granularidad,
    'tipo': tipo,
    if (productoId != null) 'producto_id': productoId,
    if (categoriaId != null) 'categoria_id': categoriaId,
  };
}

class Producto {
  final int id;
  final String nombre;
  final String? sku;

  Producto({
    required this.id,
    required this.nombre,
    this.sku,
  });

  factory Producto.fromJson(Map<String, dynamic> json) {
    return Producto(
      id: json['id'] as int,
      nombre: json['nombre'] as String,
      sku: json['sku'] as String?,
    );
  }
}
```

---

## 🔌 DATASOURCE: prediction_remote_datasource.dart

```dart
import 'package:dio/dio.dart';
import 'prediction_model.dart';

abstract class PredictionRemoteDataSource {
  Future<ForecastResponse> generarPrediccion(ForecastRequest request);
  Future<List<Producto>> obtenerProductos();
  Future<List<int>> descargarExcel(ForecastResponse data);
}

class PredictionRemoteDataSourceImpl implements PredictionRemoteDataSource {
  final Dio dio;
  static const String baseUrl = '/api/reportes';

  PredictionRemoteDataSourceImpl({required this.dio});

  @override
  Future<ForecastResponse> generarPrediccion(ForecastRequest request) async {
    try {
      final response = await dio.post(
        '$baseUrl/prediccion/',
        data: request.toJson(),
      );
      
      if (response.statusCode == 200) {
        return ForecastResponse.fromJson(response.data as Map<String, dynamic>);
      } else {
        throw Exception('Error: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error de conexión: ${e.message}');
    }
  }

  @override
  Future<List<Producto>> obtenerProductos() async {
    try {
      final response = await dio.get('$baseUrl/prediccion/productos/');
      
      if (response.statusCode == 200) {
        return List<Producto>.from(
          (response.data as List).map((p) => Producto.fromJson(p as Map<String, dynamic>))
        );
      } else {
        throw Exception('Error: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error: ${e.message}');
    }
  }

  @override
  Future<List<int>> descargarExcel(ForecastResponse data) async {
    try {
      final response = await dio.post(
        '$baseUrl/prediccion/export-excel/',
        data: {
          'predicciones': data.predicciones.map((p) => p.toJson()).toList(),
          'metricas': data.metricas,
          'confianza': data.confianza,
        },
        options: Options(responseType: ResponseType.bytes),
      );
      
      if (response.statusCode == 200) {
        return response.data as List<int>;
      } else {
        throw Exception('Error descargando: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error: ${e.message}');
    }
  }
}
```

---

## 📦 REPOSITORY: prediction_repository.dart

```dart
import 'package:dartz/dartz.dart';
import '../../domain/repositories/prediction_repository_abstract.dart';
import 'prediction_model.dart';

class PredictionRepository implements PredictionRepositoryAbstract {
  final PredictionRemoteDataSource remoteDataSource;

  PredictionRepository({required this.remoteDataSource});

  @override
  Future<Either<Exception, ForecastResponse>> generarPrediccion(
    ForecastRequest request,
  ) async {
    try {
      final result = await remoteDataSource.generarPrediccion(request);
      return Right(result);
    } catch (e) {
      return Left(Exception(e.toString()));
    }
  }

  @override
  Future<Either<Exception, List<Producto>>> obtenerProductos() async {
    try {
      final result = await remoteDataSource.obtenerProductos();
      return Right(result);
    } catch (e) {
      return Left(Exception(e.toString()));
    }
  }

  @override
  Future<Either<Exception, List<int>>> descargarExcel(
    ForecastResponse data,
  ) async {
    try {
      final result = await remoteDataSource.descargarExcel(data);
      return Right(result);
    } catch (e) {
      return Left(Exception(e.toString()));
    }
  }
}
```

---

## 🧠 BLOC: prediction_bloc.dart

```dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:dartz/dartz.dart';
import 'prediction_event.dart';
import 'prediction_state.dart';
import '../../data/models/prediction_model.dart';
import '../../data/repositories/prediction_repository.dart';

class PredictionBloc extends Bloc<PredictionEvent, PredictionState> {
  final PredictionRepository repository;

  PredictionBloc({required this.repository}) : super(PredictionInitial()) {
    on<GenerarPrediccionEvent>(_onGenerarPrediccion);
    on<CargarProductosEvent>(_onCargarProductos);
    on<DescargarExcelEvent>(_onDescargarExcel);
    on<ResetPredictionEvent>(_onReset);
  }

  Future<void> _onGenerarPrediccion(
    GenerarPrediccionEvent event,
    Emitter<PredictionState> emit,
  ) async {
    emit(PredictionLoading());
    
    final result = await repository.generarPrediccion(event.request);
    
    result.fold(
      (error) => emit(PredictionError(error.toString())),
      (data) => emit(PredictionSuccess(data)),
    );
  }

  Future<void> _onCargarProductos(
    CargarProductosEvent event,
    Emitter<PredictionState> emit,
  ) async {
    final result = await repository.obtenerProductos();
    
    result.fold(
      (error) => emit(ProductosError(error.toString())),
      (productos) => emit(ProductosLoaded(productos)),
    );
  }

  Future<void> _onDescargarExcel(
    DescargarExcelEvent event,
    Emitter<PredictionState> emit,
  ) async {
    emit(ExcelLoading());
    
    final result = await repository.descargarExcel(event.data);
    
    result.fold(
      (error) => emit(ExcelError(error.toString())),
      (bytes) => emit(ExcelSuccess(bytes, event.filename)),
    );
  }

  Future<void> _onReset(
    ResetPredictionEvent event,
    Emitter<PredictionState> emit,
  ) async {
    emit(PredictionInitial());
  }
}
```

---

## 📋 EVENTS: prediction_event.dart

```dart
abstract class PredictionEvent {}

class GenerarPrediccionEvent extends PredictionEvent {
  final ForecastRequest request;

  GenerarPrediccionEvent(this.request);
}

class CargarProductosEvent extends PredictionEvent {}

class DescargarExcelEvent extends PredictionEvent {
  final ForecastResponse data;
  final String filename;

  DescargarExcelEvent(this.data, this.filename);
}

class ResetPredictionEvent extends PredictionEvent {}
```

---

## 🎯 STATES: prediction_state.dart

```dart
abstract class PredictionState {}

class PredictionInitial extends PredictionState {}

class PredictionLoading extends PredictionState {}

class PredictionSuccess extends PredictionState {
  final ForecastResponse data;

  PredictionSuccess(this.data);
}

class PredictionError extends PredictionState {
  final String message;

  PredictionError(this.message);
}

class ProductosLoaded extends PredictionState {
  final List<Producto> productos;

  ProductosLoaded(this.productos);
}

class ProductosError extends PredictionState {
  final String message;

  ProductosError(this.message);
}

class ExcelLoading extends PredictionState {}

class ExcelSuccess extends PredictionState {
  final List<int> bytes;
  final String filename;

  ExcelSuccess(this.bytes, this.filename);
}

class ExcelError extends PredictionState {
  final String message;

  ExcelError(this.message);
}
```

---

## 🎨 WIDGETS: prediction_chart.dart

```dart
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../data/models/prediction_model.dart';

class PredictionChart extends StatelessWidget {
  final ForecastResponse data;
  final String titulo;

  const PredictionChart({
    required this.data,
    required this.titulo,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isMobile = MediaQuery.of(context).size.width < 600;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              titulo,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            SizedBox(height: 16),
            SizedBox(
              height: isMobile ? 300 : 400,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(show: true),
                  titlesData: FlTitlesData(
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: _buildXAxisLabel,
                        interval: 1,
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: _buildYAxisLabel,
                      ),
                    ),
                  ),
                  lineBarsData: [
                    // Línea histórica
                    LineChartBarData(
                      spots: _buildHistoricoSpots(),
                      isCurved: true,
                      color: Colors.blue,
                      barWidth: 2,
                      dotData: FlDotData(show: true),
                      label: 'Histórico',
                    ),
                    // Línea predicción
                    LineChartBarData(
                      spots: _buildPrediccionSpots(),
                      isCurved: true,
                      color: Colors.red,
                      barWidth: 2,
                      dashArray: [5, 5],
                      dotData: FlDotData(show: false),
                      label: 'Predicción',
                    ),
                  ],
                  borderData: FlBorderData(show: true),
                  showingTooltipIndicators: [],
                ),
              ),
            ),
            SizedBox(height: 16),
            _buildLeyenda(),
          ],
        ),
      ),
    );
  }

  List<FlSpot> _buildHistoricoSpots() {
    return data.historico.asMap().entries.map((e) {
      return FlSpot(e.key.toDouble(), e.value.valorHistorico ?? 0);
    }).toList();
  }

  List<FlSpot> _buildPrediccionSpots() {
    final offsetHistorico = data.historico.length;
    return data.predicciones.asMap().entries.map((e) {
      return FlSpot(
        (offsetHistorico + e.key).toDouble(),
        e.value.valorPredicho,
      );
    }).toList();
  }

  Widget _buildXAxisLabel(double value, TitleMeta meta) {
    final index = value.toInt();
    if (index < data.historico.length) {
      return Text(data.historico[index].periodo, style: const TextStyle(fontSize: 10));
    } else {
      final predIndex = index - data.historico.length;
      if (predIndex < data.predicciones.length) {
        return Text(data.predicciones[predIndex].periodo, style: const TextStyle(fontSize: 10));
      }
    }
    return const SizedBox();
  }

  Widget _buildYAxisLabel(double value, TitleMeta meta) {
    return Text('Bs. ${(value / 1000).toStringAsFixed(1)}k', style: const TextStyle(fontSize: 10));
  }

  Widget _buildLeyenda() {
    return Wrap(
      spacing: 16,
      children: [
        _legendaItem('Histórico', Colors.blue),
        _legendaItem('Predicción', Colors.red),
        _legendaItem('IC 95%', Colors.grey),
      ],
    );
  }

  Widget _legendaItem(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
```

---

## 📱 PAGE: predictions_page.dart

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/prediction_bloc.dart';
import '../bloc/prediction_event.dart';
import '../bloc/prediction_state.dart';
import '../widgets/filter_sheet.dart';
import '../widgets/prediction_chart.dart';
import '../widgets/prediction_table.dart';
import '../widgets/export_buttons.dart';

class PredictionsPage extends StatefulWidget {
  const PredictionsPage({Key? key}) : super(key: key);

  @override
  State<PredictionsPage> createState() => _PredictionsPageState();
}

class _PredictionsPageState extends State<PredictionsPage> {
  @override
  void initState() {
    super.initState();
    context.read<PredictionBloc>().add(CargarProductosEvent());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📈 Predicción de Ventas'),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              ElevatedButton.icon(
                onPressed: () => _mostrarFiltros(context),
                icon: const Icon(Icons.tune),
                label: const Text('Filtros'),
              ),
              const SizedBox(height: 16),
              BlocBuilder<PredictionBloc, PredictionState>(
                builder: (context, state) {
                  if (state is PredictionLoading) {
                    return const Center(child: CircularProgressIndicator());
                  } else if (state is PredictionSuccess) {
                    return Column(
                      children: [
                        PredictionChart(
                          data: state.data,
                          titulo: 'Predicción de Ventas',
                        ),
                        const SizedBox(height: 16),
                        ExportButtons(data: state.data),
                        const SizedBox(height: 16),
                        PredictionTable(predicciones: state.data.predicciones),
                      ],
                    );
                  } else if (state is PredictionError) {
                    return Center(
                      child: Column(
                        children: [
                          const Icon(Icons.error_outline, color: Colors.red, size: 48),
                          const SizedBox(height: 16),
                          Text('Error: ${state.message}'),
                        ],
                      ),
                    );
                  }
                  return Center(
                    child: Column(
                      children: [
                        Icon(Icons.trending_up, size: 48, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        const Text('Selecciona filtros y genera predicción'),
                      ],
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _mostrarFiltros(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => FilterSheet(
        onApply: (request) {
          context.read<PredictionBloc>().add(GenerarPrediccionEvent(request));
          Navigator.pop(context);
        },
      ),
    );
  }
}
```

---

## 📥 EXPORTAR: export_buttons.dart

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:share_plus/share_plus.dart';
import '../../data/models/prediction_model.dart';
import '../../bloc/prediction_bloc.dart';
import '../../bloc/prediction_event.dart';
import '../../../core/services/file_service.dart';

class ExportButtons extends StatelessWidget {
  final ForecastResponse data;

  const ExportButtons({required this.data, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            ElevatedButton.icon(
              onPressed: () => _descargarExcel(context),
              icon: const Icon(Icons.file_download),
              label: const Text('Excel'),
            ),
            ElevatedButton.icon(
              onPressed: () => _compartir(context),
              icon: const Icon(Icons.share),
              label: const Text('Compartir'),
            ),
          ],
        ),
        BlocListener<PredictionBloc, PredictionState>(
          listener: (context, state) {
            if (state is ExcelSuccess) {
              _mostrarDescargueSatisfactorio(context, state.filename);
            } else if (state is ExcelError) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Error: ${state.message}')),
              );
            }
          },
          child: const SizedBox(),
        ),
      ],
    );
  }

  void _descargarExcel(BuildContext context) {
    final filename = 'prediccion_${DateTime.now().toIso8601String().split('T')[0]}.xlsx';
    context.read<PredictionBloc>().add(DescargarExcelEvent(data, filename));
  }

  void _compartir(BuildContext context) async {
    try {
      final tabla = _generarTablaMarkdown();
      await Share.share(tabla, subject: 'Predicción de Ventas');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error compartiendo: $e')),
      );
    }
  }

  String _generarTablaMarkdown() {
    StringBuffer buffer = StringBuffer();
    buffer.writeln('# Predicción de Ventas\n');
    buffer.writeln('| Período | Valor | Confianza |');
    buffer.writeln('|---------|-------|-----------|');
    
    for (var pred in data.predicciones) {
      buffer.writeln(
        '| ${pred.periodo} | Bs. ${pred.valorPredicho.toStringAsFixed(2)} | ${(pred.confianza * 100).toStringAsFixed(1)}% |'
      );
    }
    
    return buffer.toString();
  }

  void _mostrarDescargueSatisfactorio(BuildContext context, String filename) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('✅ Descargado'),
        content: Text('Archivo guardado: $filename'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}
```

---

## 📋 TABLA: prediction_table.dart

```dart
import 'package:flutter/material.dart';
import '../../data/models/prediction_model.dart';

class PredictionTable extends StatelessWidget {
  final List<Prediccion> predicciones;

  const PredictionTable({required this.predicciones, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Período')),
          DataColumn(label: Text('Valor (Bs.)')),
          DataColumn(label: Text('IC Inferior')),
          DataColumn(label: Text('IC Superior')),
          DataColumn(label: Text('Confianza')),
        ],
        rows: predicciones
            .map(
              (p) => DataRow(
                cells: [
                  DataCell(Text(p.periodo)),
                  DataCell(Text(p.valorPredicho.toStringAsFixed(2))),
                  DataCell(Text(p.icInferior.toStringAsFixed(2))),
                  DataCell(Text(p.icSuperior.toStringAsFixed(2))),
                  DataCell(Text('${(p.confianza * 100).toStringAsFixed(1)}%')),
                ],
              ),
            )
            .toList(),
      ),
    );
  }
}
```

---

## ⬇️ SERVICIO: file_service.dart

```dart
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class FileService {
  static Future<String> guardarArchivo(List<int> bytes, String filename) async {
    final directory = await getDownloadsDirectory();
    final filePath = '${directory?.path}/$filename';
    final file = File(filePath);
    await file.writeAsBytes(bytes);
    return filePath;
  }

  static Future<bool> compartirArchivo(String filePath) async {
    final file = File(filePath);
    if (await file.exists()) {
      // Usar intent de compartir
      return true;
    }
    return false;
  }
}
```

---

## 📦 PUBSPEC.yaml - DEPENDENCIAS

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # Networking
  dio: ^5.3.0
  
  # State Management
  flutter_bloc: ^8.1.0
  
  # Modelos
  dartz: ^0.10.1
  
  # Gráficas
  fl_chart: ^0.63.0
  
  # Archivos
  path_provider: ^2.0.15
  share_plus: ^7.0.0
  
  # Local Storage
  hive: ^2.2.3
  hive_flutter: ^1.1.0
```

**Instalación:**
```bash
flutter pub get
```

---

## 🔧 INYECCIÓN DE DEPENDENCIAS

```dart
// En main.dart o setup.dart

final getIt = GetIt.instance;

void setupServiceLocator() {
  // Datasources
  getIt.registerSingleton<PredictionRemoteDataSource>(
    PredictionRemoteDataSourceImpl(dio: getIt<Dio>()),
  );

  // Repositories
  getIt.registerSingleton<PredictionRepository>(
    PredictionRepository(remoteDataSource: getIt()),
  );

  // BLoCs
  getIt.registerSingleton<PredictionBloc>(
    PredictionBloc(repository: getIt()),
  );
}

void main() {
  setupServiceLocator();
  runApp(const MyApp());
}
```

---

## 📱 NOTIFICACIONES PUSH (Futuro)

```dart
// Para alertas de predicción baja
class NotificationService {
  static Future<void> enviarAlertaVentasAltas() async {
    // Usar firebase_messaging
    // Mostrar notificación si predicción cae > 20%
  }
}
```

---

## ✅ CHECKLIST

- [ ] Crear estructura de carpetas
- [ ] Implementar modelos (prediction_model.dart)
- [ ] Implementar datasource (prediction_remote_datasource.dart)
- [ ] Implementar repository (prediction_repository.dart)
- [ ] Implementar BLoC (prediction_bloc.dart)
- [ ] Crear widgets (chart, table, filters, export)
- [ ] Crear page principal (predictions_page.dart)
- [ ] Integrar en drawer/navigation
- [ ] Testing unitario
- [ ] Testing de UI
- [ ] Testing en dispositivos reales
- [ ] Implementar file_service.dart
- [ ] Agregar dependencias en pubspec.yaml

---

## 🎯 FUNCIONALIDADES MÓVILES

✅ **Implementables:**
- Gráfica de predicción (fl_chart)
- Tabla de datos
- Filtros dinámicos
- Descarga Excel
- Compartir por email/WhatsApp
- Almacenamiento local de datos

⏳ **Futuro:**
- Notificaciones push de predicción baja
- Modo offline con caché local
- Gráfica 3D interactiva
- Export a PDF
- Biometría para acceso

---

## 📊 RESPONSIVE DESIGN MÓVIL

```dart
// Helper para responsive
class ResponsiveHelper {
  static bool isMobile(BuildContext context) =>
    MediaQuery.of(context).size.width < 600;
  
  static bool isTablet(BuildContext context) =>
    MediaQuery.of(context).size.width >= 600 && 
    MediaQuery.of(context).size.width < 1200;
}

// Uso en widgets
if (ResponsiveHelper.isMobile(context)) {
  // Layout móvil
} else if (ResponsiveHelper.isTablet(context)) {
  // Layout tablet
}
```

