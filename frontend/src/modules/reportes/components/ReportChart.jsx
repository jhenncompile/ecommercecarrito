import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function ReportChart({ data, title }) {
  if (!data || data.length === 0) return null;

  const keys = Object.keys(data[0]);
  
  // Auto-detect label key
  const labelKeyCandidates = ['mes', 'año', 'dia', 'nombre', 'categoria', 'estado', 'periodo'];
  let labelKey = keys.find(k => labelKeyCandidates.includes(k));
  if (!labelKey) {
      labelKey = keys.find(k => typeof data[0][k] === 'string') || keys[0];
  }

  // Auto-detect value key
  const valueKeyCandidates = ['total_ventas', 'total', 'cantidad_pedidos', 'cantidad_productos', 'stock', 'conteo', 'precio'];
  let valueKey = keys.find(k => valueKeyCandidates.includes(k));
  if (!valueKey) {
      valueKey = keys.find(k => typeof data[0][k] === 'number' && k !== 'id') || keys[1] || keys[0];
  }

  const formatLabel = (key) => key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');

  const formatXLabel = (key, value) => {
    if (!value) return 'N/A';
    const valStr = String(value);
    
    // Detectar si parece una fecha (e.g. 2026-05-01T00:00:00-04:00 o 2026-05-01)
    const isDate = /^\d{4}-\d{2}-\d{2}(T|$)/.test(valStr);
    
    if (isDate) {
        const date = new Date(valStr);
        if (!isNaN(date.getTime())) {
            if (key === 'mes' || key === 'month') {
                return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            }
            if (key === 'año' || key === 'year') {
                return `${date.getFullYear()}`;
            }
            if (key === 'dia' || key === 'date') {
                return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
            }
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        }
    }
    return valStr;
  };

  const chartData = {
    labels: data.map(row => formatXLabel(labelKey, row[labelKey])),
    datasets: [
      {
        label: formatLabel(valueKey),
        data: data.map(row => Number(row[valueKey]) || 0),
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderColor: '#3b82f6',
        borderWidth: 1,
        borderRadius: 4
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: {
        display: !!title,
        text: title,
        font: { size: 16 }
      }
    }
  };

  return (
    <div style={{ height: '300px', width: '100%', marginBottom: '24px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <Bar data={chartData} options={options} />
    </div>
  );
}
