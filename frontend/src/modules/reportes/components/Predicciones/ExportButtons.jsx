import React, { useState } from 'react';
import styles from '../../styles/Predicciones.module.css';
import { generatePDF, generateExcel } from 'utils/exports/exportOrchestrator';

export default function ExportButtons({ data, prediccionConfig }) {
  const [exportingExcel, setExportingExcel] = useState(false);
  const [exportingPDF, setExportingPDF] = useState(false);

  const handleDownloadExcel = async () => {
    if (!data || !data.predicciones) return;
    setExportingExcel(true);
    try {
      const title = `Predicción ${prediccionConfig?.tipo === 'ventas_totales' ? 'Global' : (prediccionConfig?.tipo || '')}`;
      await generateExcel('prediccion', null, { 
        title: title, 
        data: data 
      });
    } finally {
      setExportingExcel(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!data || !data.predicciones) return;
    setExportingPDF(true);
    try {
      const title = `Predicción ${prediccionConfig?.tipo === 'ventas_totales' ? 'Global' : (prediccionConfig?.tipo || '')}`;
      await generatePDF('prediccion', null, { 
        title: title, 
        data: data 
      });
    } finally {
      setExportingPDF(false);
    }
  };

  return (
    <div className={styles.exportButtons}>
      <button 
        onClick={handleDownloadPDF}
        disabled={exportingPDF || exportingExcel}
        style={{
          background: '#ef4444', color: 'white', padding: '8px 16px', 
          borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold'
        }}
      >
        {exportingPDF ? 'Exportando...' : '📄 Descargar Reporte PDF'}
      </button>
      
      <button 
        onClick={handleDownloadExcel}
        disabled={exportingExcel || exportingPDF}
        style={{
          background: '#10b981', color: 'white', padding: '8px 16px', 
          borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold'
        }}
      >
        {exportingExcel ? 'Exportando...' : '📥 Descargar Excel Analítico'}
      </button>
    </div>
  );
}
