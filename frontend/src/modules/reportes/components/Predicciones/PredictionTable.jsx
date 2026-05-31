import React from 'react';

export default function PredictionTable({ data }) {
  if (!data || !data.historico || !data.predicciones) return null;

  const historicoRows = data.historico.map(row => ({
    ...row,
    tipo_dato: 'H',
    valor_mostrar: row.cantidad
  }));

  const prediccionRows = data.predicciones.map(row => ({
    ...row,
    tipo_dato: 'P',
    valor_mostrar: row.cantidad_estimada
  }));

  const combinedData = [...historicoRows, ...prediccionRows];

  const formatValue = (v) => v !== null && v !== undefined ? v.toLocaleString('es-BO', {minimumFractionDigits: 2}) : '-';

  return (
    <div style={{ overflowX: 'auto', padding: '16px' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
            <th style={{ padding: '12px' }}>Período</th>
            <th style={{ padding: '12px', textAlign: 'center' }}>Tipo</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Cantidad Estimada</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Límite Inferior</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Límite Superior</th>
            <th style={{ padding: '12px', textAlign: 'center' }}>Confianza</th>
          </tr>
        </thead>
        <tbody>
          {combinedData.map((row, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid #e5e7eb', backgroundColor: row.tipo_dato === 'P' ? '#fdf2f8' : 'white' }}>
              <td style={{ padding: '12px', fontWeight: 'bold' }}>{row.periodo}</td>
              <td style={{ padding: '12px', textAlign: 'center' }}>
                {row.tipo_dato === 'H' ? 'Histórico' : 'Predicción'}
              </td>
              <td style={{ padding: '12px', textAlign: 'right', fontWeight: 'bold' }}>
                {formatValue(row.valor_mostrar)}
              </td>
              <td style={{ padding: '12px', textAlign: 'right', color: '#6b7280' }}>
                {row.tipo_dato === 'P' ? formatValue(row.ic_inferior) : '-'}
              </td>
              <td style={{ padding: '12px', textAlign: 'right', color: '#6b7280' }}>
                {row.tipo_dato === 'P' ? formatValue(row.ic_superior) : '-'}
              </td>
              <td style={{ padding: '12px', textAlign: 'center' }}>
                {row.tipo_dato === 'P' && row.confianza ? `${(row.confianza * 100).toFixed(1)}%` : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
