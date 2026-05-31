import React, { useState } from 'react';
import * as XLSX from 'xlsx';
import styles from '../../styles/Predicciones.module.css';

export default function ExportButtons({ data, chartRef, prediccionConfig }) {
  const [exporting, setExporting] = useState(false);

  const handleDownloadExcel = async () => {
    if (!data || !data.predicciones) return;
    setExporting(true);
    try {
      // 1. Convertir data a formato de Excel
      const wsData = data.predicciones.map(p => ({
        'Período': p.periodo,
        'Tipo': p.tipo_dato === 'H' ? 'Histórico' : 'Predicción',
        'Valor (Bs.)': p.valor_historico || p.valor_predicho || 0,
        'IC Inferior': p.ic_inferior || '',
        'IC Superior': p.ic_superior || '',
        'Confianza': p.confianza ? `${(p.confianza * 100).toFixed(1)}%` : ''
      }));

      const ws = XLSX.utils.json_to_sheet(wsData);
      
      // Ajustar ancho de columnas
      const wscols = [
        {wch: 15}, {wch: 15}, {wch: 20}, {wch: 15}, {wch: 15}, {wch: 15}
      ];
      ws['!cols'] = wscols;

      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Predicciones');

      // 2. Descargar archivo
      const fecha = new Date().toISOString().split('T')[0];
      XLSX.writeFile(wb, `prediccion_ventas_${fecha}.xlsx`);
    } catch (err) {
      console.error('Error exportando a Excel:', err);
      alert('Error al exportar a Excel');
    } finally {
      setExporting(false);
    }
  };

  const handleDownloadImage = () => {
    if (!chartRef || !chartRef.current) return;
    try {
      const url = chartRef.current.toBase64Image();
      const link = document.createElement('a');
      link.download = `grafica_prediccion_${new Date().toISOString().split('T')[0]}.png`;
      link.href = url;
      link.click();
    } catch (err) {
      console.error('Error exportando imagen:', err);
      alert('Error al exportar imagen');
    }
  };

  return (
    <div className={styles.exportButtons}>
      <button 
        onClick={handleDownloadExcel}
        disabled={exporting}
        style={{
          background: '#10b981', color: 'white', padding: '8px 16px', 
          borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold'
        }}
      >
        {exporting ? 'Exportando...' : '📥 Descargar Excel'}
      </button>
      
      <button 
        onClick={handleDownloadImage}
        disabled={exporting}
        style={{
          background: '#6366f1', color: 'white', padding: '8px 16px', 
          borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold'
        }}
      >
        📷 Descargar Gráfica
      </button>
    </div>
  );
}
