import React, { useRef, useState } from 'react';
import AppView from 'shared/widgets/AppView/AppView';
import PredictionFilters from '../../components/Predicciones/PredictionFilters';
import PredictionChart from '../../components/Predicciones/PredictionChart';
import PredictionTable from '../../components/Predicciones/PredictionTable';
import ExportButtons from '../../components/Predicciones/ExportButtons';
import { usePrediction } from '../../hooks/usePrediction';
import styles from '../../styles/Predicciones.module.css';
import { TrendingUp, AlertTriangle } from 'lucide-react';

export default function PredictionView() {
  const [config, setConfig] = useState(null);
  const { data, loading, error, generatePrediction } = usePrediction();
  const chartRef = useRef(null);

  const handleGenerarPrediccion = async (filterConfig) => {
    setConfig(filterConfig);
    try {
      await generatePrediction(filterConfig);
    } catch (err) {
      console.warn("Prediction generated an error, handled by usePrediction state.");
    }
  };

  return (
    <AppView 
      title="Predicciones de IA" 
      subtitle="Anticípate al futuro con estimaciones de ventas basadas en machine learning."
    >
      <div className={styles.container}>
        <PredictionFilters 
          onFilter={handleGenerarPrediccion}
          loading={loading}
        />
        
        {error && (
          <div style={{ background: '#fef2f2', color: '#b91c1c', padding: '16px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={20} />
            <span>{error}</span>
          </div>
        )}
        
        {data && (
          <>
            <div className={styles.metricsGrid}>
              <div className={styles.metricCard}>
                <div style={{ fontSize: '14px', opacity: 0.9 }}>Promedio Histórico</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                  {data.metricas?.promedio_por_periodo || 0} <span style={{ fontSize: '14px', fontWeight: 'normal' }}>/ {data.granularidad === 'anio' ? 'año' : data.granularidad}</span>
                </div>
              </div>
              <div className={styles.metricCard} style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
                <div style={{ fontSize: '14px', opacity: 0.9 }}>Datos Analizados</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                  {data.metricas?.datos_usados || 0} períodos
                </div>
              </div>
            </div>

            <div className={styles.chartSection}>
              <PredictionChart 
                data={data}
                titulo={`Predicción - ${config?.tipo === 'ventas_totales' ? 'Global' : config?.tipo}`}
                loading={loading}
                chartRef={chartRef}
              />
            </div>
            
            <ExportButtons 
              data={data}
              chartRef={chartRef}
              prediccionConfig={config}
            />
            
            <div className={styles.tableSection}>
              <PredictionTable 
                data={data}
              />
            </div>
          </>
        )}
        
        {!data && !loading && !error && (
          <div className={styles.emptyState}>
            <TrendingUp size={48} color="#9ca3af" />
            <h3>Sin predicción generada</h3>
            <p>Selecciona los parámetros deseados y haz clic en "Generar Predicción".</p>
          </div>
        )}
      </div>
    </AppView>
  );
}
