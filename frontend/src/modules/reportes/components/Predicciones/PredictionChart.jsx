import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function PredictionChart({ data, titulo, loading, chartRef }) {
  if (loading) return null;
  if (!data || !data.historico || !data.predicciones) return null;

  const historico = [...data.historico];
  const prediccion = [...data.predicciones];

  // Para que la línea se conecte con el último punto histórico
  if (historico.length > 0 && prediccion.length > 0) {
    const lastHistorico = { ...historico[historico.length - 1] };
    lastHistorico.cantidad_estimada = lastHistorico.cantidad;
    lastHistorico.ic_inferior = lastHistorico.cantidad;
    lastHistorico.ic_superior = lastHistorico.cantidad;
    prediccion.unshift(lastHistorico);
  }

  const allLabels = Array.from(new Set([
    ...historico.map(p => p.periodo),
    ...prediccion.map(p => p.periodo)
  ])).sort();

  const formatValue = (v) => v !== null && v !== undefined ? v.toLocaleString('es-BO') : '';

  const chartData = {
    labels: allLabels,
    datasets: [
      {
        label: 'Histórico',
        data: allLabels.map(label => {
          const p = historico.find(h => h.periodo === label);
          return p ? p.cantidad : null;
        }),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: false,
        pointRadius: 4,
        tension: 0.3
      },
      {
        label: 'Predicción',
        data: allLabels.map(label => {
          const p = prediccion.find(pr => pr.periodo === label);
          return p ? p.cantidad_estimada : null;
        }),
        borderColor: '#ef4444',
        borderDash: [5, 5],
        borderWidth: 2,
        fill: false,
        pointRadius: 4,
        tension: 0.3
      },
      {
        label: 'Límite Inferior',
        data: allLabels.map(label => {
          const p = prediccion.find(pr => pr.periodo === label);
          return p ? p.ic_inferior : null;
        }),
        borderColor: 'transparent',
        backgroundColor: 'rgba(156, 163, 175, 0.2)',
        fill: '+1', // Fill to next dataset
        pointRadius: 0,
        tension: 0.3
      },
      {
        label: 'Límite Superior',
        data: allLabels.map(label => {
          const p = prediccion.find(pr => pr.periodo === label);
          return p ? p.ic_superior : null;
        }),
        borderColor: 'transparent',
        backgroundColor: 'rgba(156, 163, 175, 0.2)',
        fill: false,
        pointRadius: 0,
        tension: 0.3
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { font: { size: 12, weight: 'bold' } },
        filter: (item) => !item.text.startsWith('Límite') // Ocultar legendas de límites si se desea
      },
      title: {
        display: !!titulo,
        text: titulo,
        font: { size: 16 }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || '';
            if (label.startsWith('Límite')) return null;
            return `${label}: ${formatValue(context.parsed.y)}`;
          }
        }
      }
    },
    scales: {
      y: {
        ticks: { callback: (v) => formatValue(v) }
      }
    }
  };

  return <Line ref={chartRef} data={chartData} options={options} />;
}
