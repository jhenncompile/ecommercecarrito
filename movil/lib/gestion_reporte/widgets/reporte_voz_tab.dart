import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:excel/excel.dart' as excel;
import 'package:open_filex/open_filex.dart';
import 'package:intl/intl.dart';

import '../../core/theme/app_colors.dart';
import '../../core/widgets/buttons/app_button.dart';
import '../../core/widgets/cards/app_table_card.dart';
import '../repositories/report_repository.dart';

class ReporteVozTab extends StatefulWidget {
  const ReporteVozTab({super.key});

  @override
  State<ReporteVozTab> createState() => _ReporteVozTabState();
}

class _ReporteVozTabState extends State<ReporteVozTab> {
  bool _isRecording = false;
  bool _isLoading = false;
  bool _isUpgrading = false;
  Map<String, dynamic>? _result;
  String? _error;

  final ReportRepository _reportRepository = ReportRepository();
  final AudioRecorder _audioRecorder = AudioRecorder();

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    try {
      if (await Permission.microphone.request().isGranted) {
        final directory = await getTemporaryDirectory();
        final path = '${directory.path}/query_${DateTime.now().millisecondsSinceEpoch}.m4a';

        const config = RecordConfig(encoder: AudioEncoder.aacLc);
        await _audioRecorder.start(config, path: path);

        setState(() {
          _isRecording = true;
          _error = null;
        });
      } else {
        setState(() => _error = 'Permiso de micrófono denegado.');
      }
    } catch (e) {
      setState(() => _error = 'Error al iniciar grabación: $e');
    }
  }

  Future<void> _stopRecording() async {
    try {
      final path = await _audioRecorder.stop();
      setState(() => _isRecording = false);

      if (path != null) {
        _sendAudio(path);
      }
    } catch (e) {
      setState(() => _error = 'Error al detener grabación: $e');
    }
  }

  Future<void> _sendAudio(String filePath) async {
    setState(() {
      _isLoading = true;
      _result = null;
      _error = null;
    });

    try {
      final result = await _reportRepository.sendVoiceQuery(filePath);
      setState(() {
        _result = result;
        _isLoading = false;
      });
      try {
        await File(filePath).delete();
      } catch (_) {}
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  Future<void> _exportToPDF() async {
    if (_result == null || _result!['results'] == null) return;
    final results = _result!['results'] as List;
    if (results.isEmpty) return;

    final pdf = pw.Document();
    final List<String> headers = results[0].keys.map<String>((k) => _formatHeader(k.toString())).toList();
    final List<List<dynamic>> data = results.map<List<dynamic>>((row) => row.values.map((v) => v.toString()).toList()).toList();

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        build: (context) => [
          pw.Header(
            level: 0,
            child: pw.Text("Reporte de Consulta Inteligente IA", style: pw.TextStyle(fontSize: 24, fontWeight: pw.FontWeight.bold, color: PdfColors.blue900)),
          ),
          pw.Text("Lo que entendí: \"${_result!['prompt']}\"", style: const pw.TextStyle(fontSize: 12, color: PdfColors.grey700)),
          pw.SizedBox(height: 10),
          pw.Text("Generado el: ${DateFormat('dd/MM/yyyy HH:mm').format(DateTime.now())}"),
          pw.Text("Total registros: ${results.length}"),
          pw.SizedBox(height: 20),
          pw.TableHelper.fromTextArray(
            headers: headers,
            data: data,
            headerStyle: pw.TextStyle(fontWeight: pw.FontWeight.bold, color: PdfColors.white),
            headerDecoration: const pw.BoxDecoration(color: PdfColors.blueGrey800),
            cellAlignment: pw.Alignment.centerLeft,
            oddRowDecoration: const pw.BoxDecoration(color: PdfColors.grey100),
          ),
        ],
      ),
    );

    final directory = await getApplicationDocumentsDirectory();
    final file = File("${directory.path}/reporte_ia_${DateTime.now().millisecondsSinceEpoch}.pdf");
    await file.writeAsBytes(await pdf.save());
    
    await OpenFilex.open(file.path);
  }

  Future<void> _exportToExcel() async {
    if (_result == null || _result!['results'] == null) return;
    final results = _result!['results'] as List;
    if (results.isEmpty) return;

    var excelBook = excel.Excel.createExcel();
    excel.Sheet sheetObject = excelBook['Reporte IA'];
    excelBook.delete('Sheet1');

    final List<String> headers = results[0].keys.map<String>((k) => _formatHeader(k.toString())).toList();
    sheetObject.appendRow(headers.map((h) => excel.TextCellValue(h)).toList());

    for (var row in results) {
      sheetObject.appendRow(row.values.map((v) => excel.TextCellValue(v.toString())).toList());
    }

    final directory = await getApplicationDocumentsDirectory();
    final filePath = "${directory.path}/reporte_ia_${DateTime.now().millisecondsSinceEpoch}.xlsx";
    final bytes = excelBook.encode();
    if (bytes != null) {
      File(filePath)
        ..createSync(recursive: true)
        ..writeAsBytesSync(bytes);
      
      await OpenFilex.open(filePath);
    }
  }

  String _formatHeader(String key) {
    return key.replaceFirst(key[0], key[0].toUpperCase()).replaceAll('_', ' ');
  }

  @override
  Widget build(BuildContext context) {
    final results = _result?['results'] as List?;
    final hasResults = results != null && results.isNotEmpty;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Widget de voz
        Container(
          padding: const EdgeInsets.all(25),
          decoration: BoxDecoration(
            color: AppColors.bgCard,
            borderRadius: BorderRadius.circular(15),
            border: Border.all(color: _isRecording ? AppColors.danger : AppColors.border),
            boxShadow: [
              if (_isRecording)
                BoxShadow(color: AppColors.danger.withOpacity(0.2), blurRadius: 10, spreadRadius: 2)
            ],
          ),
          child: Column(
            children: [
              LayoutBuilder(
                builder: (context, cardConstraints) {
                  final isSmall = cardConstraints.maxWidth < 500;
                  if (isSmall) {
                    return Column(
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: _isRecording ? AppColors.danger.withOpacity(0.1) : AppColors.accentTeal.withOpacity(0.1),
                                shape: BoxShape.circle,
                              ),
                              child: Icon(
                                _isRecording ? Icons.stop : Icons.mic,
                                color: _isRecording ? AppColors.danger : AppColors.accentTeal,
                                size: 30,
                              ),
                            ),
                            const SizedBox(width: 15),
                            const Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('Asistente de Voz', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppColors.primaryDark)),
                                  Text('Habla para consultar...', style: TextStyle(color: AppColors.textMuted, fontSize: 13)),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: AppButton.add(
                            label: _isRecording ? 'Detener' : (_isLoading ? 'Analizando...' : 'Hablar'),
                            icon: _isRecording ? Icons.square : Icons.mic,
                            color: _isRecording ? AppColors.danger : AppColors.accentTeal,
                            onPressed: _isLoading ? null : (_isRecording ? _stopRecording : _startRecording),
                          ),
                        ),
                      ],
                    );
                  }
                  return Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: _isRecording ? AppColors.danger.withOpacity(0.1) : AppColors.accentTeal.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          _isRecording ? Icons.stop : Icons.mic,
                          color: _isRecording ? AppColors.danger : AppColors.accentTeal,
                          size: 30,
                        ),
                      ),
                      const SizedBox(width: 15),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Asistente de Voz', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppColors.primaryDark)),
                            Text('Habla para consultar ventas, stock o clientes.', style: TextStyle(color: AppColors.textMuted, fontSize: 13)),
                          ],
                        ),
                      ),
                      AppButton.add(
                        label: _isRecording ? 'Detener' : (_isLoading ? 'Analizando...' : 'Hablar'),
                        icon: _isRecording ? Icons.square : Icons.mic,
                        color: _isRecording ? AppColors.danger : AppColors.accentTeal,
                        onPressed: _isLoading ? null : (_isRecording ? _stopRecording : _startRecording),
                      ),
                    ],
                  );
                }
              ),
              if (_isLoading)
                const Padding(
                  padding: EdgeInsets.only(top: 20),
                  child: LinearProgressIndicator(color: AppColors.accentTeal, backgroundColor: AppColors.bgLight),
                ),
            ],
          ),
        ),

        if (_error != null)
          Padding(
            padding: const EdgeInsets.only(top: 20),
            child: _error!.contains('PLAN_REQUIRED')
                ? Container(
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
                        const Text('Mejora tu plan para acceder a consultas por voz con IA.', textAlign: TextAlign.center, style: TextStyle(color: Colors.white)),
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
                                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Plan mejorado con éxito. Ya puedes grabar tu voz.')));
                                  setState(() {
                                    _error = null;
                                  });
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
                : Container(
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
          ),

        // Resultados
        if (_result != null) ...[
          const SizedBox(height: 30),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(color: AppColors.bgLight, borderRadius: BorderRadius.circular(15), border: Border.all(color: AppColors.border)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Lo que entendí:', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textMuted, fontSize: 12)),
                const SizedBox(height: 5),
                Text('"${_result!['prompt']}"', style: const TextStyle(fontSize: 16, fontStyle: FontStyle.italic, color: AppColors.primaryDark)),
                if (hasResults) ...[
                  const SizedBox(height: 20),
                  Row(
                    children: [
                      Expanded(
                        child: AppButton.add(
                          label: 'Exportar PDF',
                          icon: Icons.picture_as_pdf,
                          onPressed: _exportToPDF,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: AppButton.add(
                          label: 'Exportar Excel',
                          icon: Icons.table_view,
                          color: Colors.green[700]!,
                          onPressed: _exportToExcel,
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 20),
          if (hasResults)
            AppTableCard(
              title: 'Resultados (${results.length})',
              columns: results[0].keys.map<String>((k) => _formatHeader(k.toString())).toList(),
              rows: results.map<List<Widget>>((row) {
                return (row.values as Iterable).map<Widget>((v) => Text(v.toString())).toList();
              }).toList(),
            )
          else
            const Center(child: Padding(padding: EdgeInsets.all(40), child: Text('No se encontraron registros.'))),
        ],

        if (_result == null && !_isLoading && _error == null)
          const Padding(
            padding: EdgeInsets.only(top: 40),
            child: Center(
              child: Column(
                children: [
                  Icon(Icons.auto_awesome, size: 50, color: AppColors.textMuted),
                  SizedBox(height: 10),
                  Text('Prueba diciendo:', style: TextStyle(color: AppColors.textMuted)),
                  Text('"Ventas totales de hoy"', style: TextStyle(color: AppColors.accentTeal, fontWeight: FontWeight.bold)),
                  Text('"Productos con stock crítico"', style: TextStyle(color: AppColors.accentTeal, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
          ),
      ],
    );
  }
}
