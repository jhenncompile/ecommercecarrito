import React from 'react';

// Un selector de producto básico por ahora, para cumplir con el contrato visual
export default function ProductSelector({ productos = [], selected = [], onChange, maxSelection = 5, loading }) {
  // TODO: Implementar react-select o similar para búsqueda real
  return (
    <div>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
        Seleccionar Producto(s)
      </label>
      <select 
        multiple
        value={selected}
        onChange={(e) => {
          const options = [...e.target.selectedOptions];
          const values = options.map(opt => opt.value);
          if (values.length <= maxSelection) {
            onChange(values);
          }
        }}
        disabled={loading}
        style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', height: '80px' }}
      >
        {productos.map(p => (
          <option key={p.id} value={p.id}>{p.nombre}</option>
        ))}
      </select>
      <small style={{ color: '#6b7280' }}>
        Seleccionados: {selected.length} de {maxSelection}
      </small>
    </div>
  );
}
