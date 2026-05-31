import React, { useState, useEffect } from 'react';
import styles from '../../styles/Predicciones.module.css';
import api from 'core/services/api';

export default function PredictionFilters({ onFilter, loading, disabled, maxMesesDisponibles = 12 }) {
  const [dataHistorica, setDataHistorica] = useState('12');
  const [unidadHistorica, setUnidadHistorica] = useState('meses');
  const [todoHistorico, setTodoHistorico] = useState(false);

  const [prediccionPeriodo, setPrediccionPeriodo] = useState('3');
  const [unidadPrediccion, setUnidadPrediccion] = useState('meses');

  const [granularidad, setGranularidad] = useState('mes');
  const [tipo, setTipo] = useState('ventas_totales');

  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [productoId, setProductoId] = useState('');
  const [categoriaId, setCategoriaId] = useState('');
  const [loadingOpts, setLoadingOpts] = useState(false);

  useEffect(() => {
    if (tipo === 'por_producto' && productos.length === 0) {
      setLoadingOpts(true);
      api.get('reportes/prediccion/productos/')
        .then(res => {
          setProductos(res.data);
          if (res.data.length > 0) setProductoId(res.data[0].id);
        })
        .catch(err => console.error(err))
        .finally(() => setLoadingOpts(false));
    }
    if (tipo === 'por_categoria' && categorias.length === 0) {
      setLoadingOpts(true);
      api.get('reportes/prediccion/categorias/')
        .then(res => {
          setCategorias(res.data);
          if (res.data.length > 0) setCategoriaId(res.data[0].id);
        })
        .catch(err => console.error(err))
        .finally(() => setLoadingOpts(false));
    }
  }, [tipo]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const parsedHist = parseInt(dataHistorica, 10) || 12;
    const histMeses = todoHistorico ? 999 : (unidadHistorica === 'años' ? parsedHist * 12 : parsedHist);
    const parsedPred = parseInt(prediccionPeriodo, 10) || 3;
    const predMeses = unidadPrediccion === 'años' ? parsedPred * 12 : parsedPred;
    
    const filterConfig = {
      data_historica_meses: histMeses,
      prediccion_meses: predMeses,
      granularidad,
      tipo
    };
    if (tipo === 'por_producto' && productoId) filterConfig.producto_id = parseInt(productoId, 10);
    if (tipo === 'por_categoria' && categoriaId) filterConfig.categoria_id = parseInt(categoriaId, 10);
    
    onFilter(filterConfig);
  };

  return (
    <form className={styles.filtersSection} onSubmit={handleSubmit}>
      <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#1f2937' }}>Configuración de la Predicción</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <label style={{ fontWeight: 'bold', fontSize: '14px', color: '#374151' }}>
              Histórico a analizar
            </label>
            <label style={{ fontSize: '12px', color: '#3b82f6', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <input 
                type="checkbox" 
                checked={todoHistorico}
                onChange={(e) => setTodoHistorico(e.target.checked)}
              />
              Todo
            </label>
          </div>
          <div style={{ display: 'flex', gap: '8px', opacity: todoHistorico ? 0.5 : 1 }}>
            <input 
              type="number"
              min="1"
              max="100"
              value={dataHistorica}
              onChange={(e) => setDataHistorica(e.target.value)}
              disabled={disabled || loading || todoHistorico}
              style={{ width: '60%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', color: '#1f2937', backgroundColor: '#f9fafb' }}
            />
            <select
              value={unidadHistorica}
              onChange={(e) => setUnidadHistorica(e.target.value)}
              disabled={disabled || loading || todoHistorico}
              style={{ width: '40%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', color: '#1f2937', backgroundColor: '#f9fafb' }}
            >
              <option value="meses">Meses</option>
              <option value="años">Años</option>
            </select>
          </div>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', fontSize: '14px', color: '#374151' }}>
            Período a predecir
          </label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input 
              type="number"
              min="1"
              max="60"
              value={prediccionPeriodo}
              onChange={(e) => setPrediccionPeriodo(e.target.value)}
              disabled={disabled || loading}
              style={{ width: '60%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', color: '#1f2937', backgroundColor: '#f9fafb' }}
            />
            <select
              value={unidadPrediccion}
              onChange={(e) => setUnidadPrediccion(e.target.value)}
              disabled={disabled || loading}
              style={{ width: '40%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', color: '#1f2937', backgroundColor: '#f9fafb' }}
            >
              <option value="meses">Meses</option>
              <option value="años">Años</option>
            </select>
          </div>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', fontSize: '14px', color: '#374151' }}>
            Granularidad
          </label>
          <select 
            value={granularidad} 
            onChange={(e) => setGranularidad(e.target.value)}
            disabled={disabled || loading}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', color: '#1f2937', backgroundColor: '#f9fafb' }}
          >
            <option value="dia">Diaria</option>
            <option value="semana">Semanal</option>
            <option value="mes">Mensual</option>
            <option value="año">Anual</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', fontSize: '14px', color: '#374151' }}>
            Tipo de Predicción
          </label>
          <select 
            value={tipo} 
            onChange={(e) => setTipo(e.target.value)}
            disabled={disabled || loading}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', color: '#1f2937', backgroundColor: '#f9fafb' }}
          >
            <option value="ventas_totales">Ventas Globales</option>
            <option value="por_producto">Por Producto</option>
            <option value="por_categoria">Por Categoría</option>
          </select>
        </div>

        {tipo === 'por_producto' && (
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', fontSize: '14px', color: '#374151' }}>
              Seleccionar Producto
            </label>
            <select 
              value={productoId} 
              onChange={(e) => setProductoId(e.target.value)}
              disabled={disabled || loading || loadingOpts}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', color: '#1f2937', backgroundColor: '#f9fafb' }}
            >
              {loadingOpts && <option value="">Cargando...</option>}
              {!loadingOpts && productos.map(p => (
                <option key={p.id} value={p.id}>{p.nombre}</option>
              ))}
            </select>
          </div>
        )}

        {tipo === 'por_categoria' && (
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', fontSize: '14px', color: '#374151' }}>
              Seleccionar Categoría
            </label>
            <select 
              value={categoriaId} 
              onChange={(e) => setCategoriaId(e.target.value)}
              disabled={disabled || loading || loadingOpts}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', color: '#1f2937', backgroundColor: '#f9fafb' }}
            >
              {loadingOpts && <option value="">Cargando...</option>}
              {!loadingOpts && categorias.map(c => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>
          </div>
        )}

      </div>

      <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
        <span style={{ fontSize: '12px', color: '#6b7280', alignSelf: 'center' }}>
          * Se requieren mínimo 3 meses de datos históricos
        </span>
        <button 
          type="submit" 
          disabled={disabled || loading}
          style={{ 
            background: '#3b82f6', color: 'white', padding: '8px 24px', 
            borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold',
            opacity: disabled || loading ? 0.7 : 1
          }}
        >
          {loading ? 'Generando...' : 'Generar Predicción'}
        </button>
      </div>
    </form>
  );
}
