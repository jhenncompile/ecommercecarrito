# Datos de Implementación - FRONTEND

## 📁 Estructura de Carpetas

```
frontend/src/modules/reportes/
├── views/
│   └── ReportesView.jsx                      # Vista principal (YA EXISTE)
│
├── components/
│   ├── ReportesEstaticos.jsx                 # (YA EXISTE)
│   ├── ReporteDinamicoBuilder.jsx            # (YA EXISTE)
│   │
│   └── [NUEVO] Predicciones/
│       ├── PredictionFilters.jsx             # Controles: período, granularidad, tipo
│       ├── PredictionChart.jsx               # Gráfica con Chart.js
│       ├── PredictionTable.jsx               # Tabla de resultados
│       ├── ProductSelector.jsx               # Selector multi-producto
│       ├── ExportButtons.jsx                 # Botones descargar Excel/PNG
│       └── PredictionView.jsx                # Componente contenedor
│
├── styles/
│   └── [NUEVO]
│       └── Predicciones.module.css
│
└── hooks/
    └── [NUEVO]
        └── usePrediction.js                  # Hook reutilizable
```

---

## 🎛️ COMPONENTES DETALLADOS

### 1. PredictionFilters.jsx
**Responsabilidad:** Capturar parámetros de predicción del usuario

**Props:**
```jsx
{
  onFilter: (config) => void,
  loading: boolean,
  disabled: boolean
}
```

**Estado interno:**
```jsx
{
  dataHistorica: "24",        // 6, 12, 24, "all"
  prediccionPeriodo: "12",    // 1, 3, 6, 12, 24
  granularidad: "mes",        // dia, semana, mes, año
  tipo: "ventas_totales",     // ventas_totales, por_producto, por_categoria
  productoId: null,           // Solo si tipo === "por_producto"
}
```

**Elementos UI:**
- Combo boxes con iconos (📅 Período histórico)
- Radio buttons para granularidad
- Selector de productos (multi-select si tipo = "por_producto")
- Botón primario "Generar Predicción" + loading spinner
- Info tooltip: "Se necesitan mínimo 3 meses de datos"

---

### 2. PredictionChart.jsx
**Responsabilidad:** Renderizar gráfica de línea con predicción

**Props:**
```jsx
{
  data: {
    historico: Array<{fecha: string, valor: number}>,
    prediccion: Array<{fecha: string, valor: number, ic_inferior: number, ic_superior: number}>,
    confianza: number
  },
  titulo: string,
  loading: boolean,
  onDownload: () => void
}
```

**Librería:** Chart.js + react-chartjs-2

**Elementos:**
- **Eje X:** Períodos (meses/semanas/días)
- **Eje Y:** Monto en moneda local (BOB)
- **Línea azul:** Datos históricos (línea sólida)
- **Línea roja punteada:** Predicción
- **Área gris:** Intervalo de confianza (fill between IC)
- **Tooltip:** Al hover → Período | Valor | Confianza %

**Código base:**
```jsx
const chartConfig = {
  type: 'line',
  options: {
    responsive: true,
    plugins: {
      legend: {
        labels: { font: { size: 12, weight: 'bold' } }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const { dataset, parsed } = context;
            return `${dataset.label}: Bs. ${parsed.y.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      y: {
        ticks: { callback: (v) => `Bs. ${v.toLocaleString()}` }
      }
    }
  },
  data: {
    labels: historico.map(h => h.fecha),
    datasets: [
      {
        label: 'Histórico',
        data: historico.map(h => h.valor),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: false,
        pointRadius: 3
      },
      {
        label: 'Predicción',
        data: prediccion.map(p => p.valor),
        borderColor: '#ef4444',
        borderDash: [5, 5],
        borderWidth: 2,
        fill: false,
        pointRadius: 0
      },
      {
        label: 'IC 95%',
        data: prediccion.map(p => (p.ic_superior + p.ic_inferior) / 2),
        backgroundColor: 'rgba(156, 163, 175, 0.2)',
        borderColor: 'transparent',
        fill: true,
        pointRadius: 0
      }
    ]
  }
};
```

---

### 3. PredictionTable.jsx
**Responsabilidad:** Mostrar tabla de predicciones

**Columnas:**
```jsx
[
  { key: 'periodo', label: 'Período', align: 'center' },
  { key: 'tipo_dato', label: 'Tipo', align: 'center', render: (v) => v === 'H' ? '📊 Histórico' : '🔮 Predicción' },
  { key: 'valor', label: 'Valor (Bs.)', align: 'right', render: (v) => v.toLocaleString('es-BO', {maximumFractionDigits: 2}) },
  { key: 'ic_inferior', label: 'IC Inferior', align: 'right' },
  { key: 'ic_superior', label: 'IC Superior', align: 'right' },
  { key: 'confianza', label: 'Confianza', align: 'center', render: (v) => `${(v*100).toFixed(1)}%` },
  { key: 'variacion', label: 'Variación %', align: 'center', render: (v) => {
    const icon = v > 0 ? '📈' : '📉';
    return `${icon} ${Math.abs(v).toFixed(2)}%`;
  }}
]
```

**Interactividad:**
- Scroll horizontal en móvil
- Click en fila → expandir detalles
- Sort por período, valor, confianza
- Filtro búsqueda por período

---

### 4. ProductSelector.jsx
**Responsabilidad:** Seleccionar múltiples productos

**Props:**
```jsx
{
  productos: Array<{id, nombre, sku}>,
  selected: Array<id>,
  onChange: (ids) => void,
  maxSelection: 5,
  loading: boolean
}
```

**UI:**
- Campo search con autocomplete
- Chips de productos seleccionados
- Botón "Limpiar selección"
- Contador: "3 de 5 productos"

---

### 5. ExportButtons.jsx
**Responsabilidad:** Descargas de reportes

**Props:**
```jsx
{
  data: PredictionData,
  chartRef: React.Ref,
  loading: boolean,
  prediccionConfig: object
}
```

**Botones:**
1. **Descargar Excel**
   - Llama: `POST /api/reportes/prediccion/export-excel/`
   - Descarga: `prediccion_ventas_${fecha}.xlsx`
   
2. **Descargar Gráfica (PNG)**
   - Usa `chart.toBase64Image()`
   - Crea canvas con metadata
   - Descarga: `prediccion_grafica_${fecha}.png`

3. **Copiar a Clipboard**
   - Copia tabla como markdown
   - Muestra toast: "Copiado ✓"

**Código descarga Excel:**
```jsx
const handleDownloadExcel = async () => {
  try {
    const response = await api.post('/reportes/prediccion/export-excel/', {
      predicciones: data.predicciones,
      config: prediccionConfig,
      metricas: data.metricas
    }, { responseType: 'blob' });
    
    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `prediccion_ventas_${new Date().toISOString().split('T')[0]}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    setError('Error descargando archivo');
  }
};
```

---

### 6. PredictionView.jsx
**Responsabilidad:** Orquestador principal

**Estructura:**
```jsx
export default function PredictionView() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const chartRef = useRef();

  const handleGenerarPrediccion = async (filterConfig) => {
    setLoading(true);
    try {
      const response = await api.post('/api/reportes/prediccion/', filterConfig);
      setData(response.data);
      setConfig(filterConfig);
    } catch (err) {
      setError(err.response?.data?.error || 'Error generando predicción');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <PredictionFilters 
        onFilter={handleGenerarPrediccion}
        loading={loading}
      />
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {data && (
        <>
          <PredictionChart 
            data={data}
            titulo={`Predicción - ${config.tipo}`}
            loading={loading}
            chartRef={chartRef}
          />
          
          <ExportButtons 
            data={data}
            chartRef={chartRef}
            prediccionConfig={config}
          />
          
          <PredictionTable 
            data={data.predicciones}
            metricas={data.metricas}
          />
        </>
      )}
      
      {!data && !loading && (
        <EmptyState 
          icon={<BarChart3 size={48} />}
          title="Sin predicción"
          subtitle="Selecciona parámetros y haz clic en 'Generar Predicción'"
        />
      )}
    </div>
  );
}
```

---

## 🪝 Hook: usePrediction.js

**Responsabilidad:** Lógica reutilizable de predicciones

```javascript
export function usePrediction() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cache, setCache] = useState({});

  const generatePrediction = useCallback(async (config) => {
    const cacheKey = JSON.stringify(config);
    if (cache[cacheKey]) {
      setData(cache[cacheKey]);
      return cache[cacheKey];
    }

    setLoading(true);
    try {
      const response = await api.post('/api/reportes/prediccion/', config);
      setData(response.data);
      setCache(prev => ({ ...prev, [cacheKey]: response.data }));
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Error');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [cache]);

  return { data, loading, error, generatePrediction };
}
```

---

## 🎨 Estilos: Predicciones.module.css

```css
.container {
  padding: 24px;
  display: grid;
  gap: 24px;
}

.filtersSection {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border-left: 4px solid #3b82f6;
}

.chartSection {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  position: relative;
  height: 450px;
}

.tableSection {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.metricsGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.metricCard {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.exportButtons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 20px 0;
}

@media (max-width: 768px) {
  .chartSection {
    height: 300px;
  }
  
  .filtersSection {
    flex-direction: column;
  }
  
  .exportButtons {
    flex-direction: column;
  }
  
  .exportButtons button {
    width: 100%;
  }
}
```

---

## 🔌 Integración en ReportesView.jsx

**Cambios necesarios:**
```jsx
// Agregar nuevo tab
const tabs = [
  { id: 'estaticos', label: '📊 Reportes Básicos', icon: BarChart3 },
  { id: 'dinamicos', label: '⚙️ Reportes Dinámicos', icon: Settings2 },
  { id: 'predicciones', label: '📈 Predicciones IA', icon: TrendingUp }  // NUEVO
];

// En render:
{activeTab === 'predicciones' && <PredictionView />}
```

---

## 📊 API ENDPOINTS ESPERADOS (Backend debe proporcionar)

```
POST /api/reportes/prediccion/
  Request: {
    data_historica_meses: 24,
    prediccion_meses: 12,
    granularidad: "mes",
    tipo: "ventas_totales" | "por_producto" | "por_categoria",
    producto_id?: integer,
    categoria_id?: integer
  }
  
  Response: {
    predicciones: Array<{
      periodo: string,
      valor_historico?: number,
      valor_predicho: number,
      ic_inferior: number,
      ic_superior: number,
      confianza: number
    }>,
    metricas: {
      r_squared: number,
      aic: number,
      rmse: number,
      periodo_analisis: string,
      datos_usados: integer
    }
  }

POST /api/reportes/prediccion/export-excel/
  Request: { predicciones: Array, config: object, metricas: object }
  Response: Blob (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

GET /api/reportes/prediccion/productos/
  Response: Array<{ id, nombre, sku }>
```

---

## 📦 DEPENDENCIAS NPM NECESARIAS

```json
{
  "chart.js": "^4.4.0",
  "react-chartjs-2": "^5.2.0",
  "xlsx": "^0.18.5",
  "html2canvas": "^1.4.1"
}
```

**Instalación:**
```bash
npm install chart.js react-chartjs-2 xlsx html2canvas
```

---

## ✅ CHECKLIST DE DESARROLLO

- [ ] Crear estructura de carpetas
- [ ] Implementar PredictionFilters.jsx
- [ ] Implementar PredictionChart.jsx con Chart.js
- [ ] Implementar PredictionTable.jsx
- [ ] Implementar ProductSelector.jsx
- [ ] Implementar ExportButtons.jsx
- [ ] Crear hook usePrediction.js
- [ ] Crear estilos Predicciones.module.css
- [ ] Integrar tab en ReportesView.jsx
- [ ] Testing componentes
- [ ] Testing responsivo (móvil)
- [ ] Documentation de APIs esperadas

---

## 📱 RESPONSIVE DESIGN

**Breakpoints:**
- 📱 Mobile: < 640px (stack vertical)
- 📱 Tablet: 640px - 1024px (2 columnas)
- 🖥️ Desktop: > 1024px (layout full)

**Consideraciones:**
- Gráfica: Height adaptativo (300px móvil, 450px desktop)
- Tabla: Scroll horizontal en móvil
- Botones: Full width en móvil
- Filtros: Collapsible en móvil (bottom sheet)

