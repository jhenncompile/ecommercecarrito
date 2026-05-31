import React, { useState } from 'react';
import {
  BarChart3, LineChart, PieChart, LayoutDashboard,
  GripVertical, Trash2, Download, Filter, FolderHeart,
  Plus, Table as TableIcon, Activity, Edit2, Check,
  FileSpreadsheet, FileText, ChevronDown, TrendingUp,
  Target, CircleDashed, Layers, Maximize2, Minimize2,
  AlignLeft, ListFilter, BarChart2, ShoppingBag, Users,
  CalendarDays, Radar, ArrowDownToLine, Settings, Calendar
} from 'lucide-react';

import { useEffect } from 'react';
import api from 'core/services/api';
import { Spinner } from 'shared/components';
import { generatePDF, generateExcel } from 'utils/exports/exportOrchestrator';
import WidgetConfigModal from './WidgetConfigModal';
import styles from './DashboardBuilder.module.css';

import {
  CustomBarChart, CustomLineChart, CustomPieChart, KPICard, CustomTable,
  CustomWaterfallChart, CustomCohortAnalysis, CustomHeatmap, CustomRadarChart,
  SparklineKPI, CustomFunnelChart, CustomStackedBarChart, CustomAreaChart,
  CustomDoughnutChart, CustomHorizontalBarChart
} from './DashboardWidgets';

// ─── MOCK DATA ────────────────────────────────────────────────────────────────
const generateData = (m = 1) => [
  { label: 'Ene', value: 150 * m }, { label: 'Feb', value: 200 * m },
  { label: 'Mar', value: 175 * m }, { label: 'Abr', value: 280 * m },
  { label: 'May', value: 310 * m }, { label: 'Jun', value: 260 * m },
];
const generatePieData = () => [
  { label: 'Electrónica', value: 40, color: '#3b82f6' },
  { label: 'Ropa', value: 35, color: '#10b981' },
  { label: 'Hogar', value: 25, color: '#f59e0b' },
];
const generateFunnelData = () => [
  { label: 'Visitas', value: 10000 }, { label: 'Carrito', value: 2500 },
  { label: 'Checkout', value: 800 },  { label: 'Compras', value: 300 },
];
const generateStackedData = () => [
  { label: 'Ene', segment1: 100, segment2: 50, segment3: 20 },
  { label: 'Feb', segment1: 120, segment2: 70, segment3: 30 },
  { label: 'Mar', segment1: 90,  segment2: 40, segment3: 50 },
];
const generateWaterfallData = () => [
  { label: 'Ventas', value: 120000, type: 'positive' },
  { label: 'Costos', value: -45000, type: 'negative' },
  { label: 'Marketing', value: -15000, type: 'negative' },
  { label: 'Neto', value: 60000, type: 'total' },
];
const generateCohortData = () => [
  { cohort: 'Ene', data: [100, 60, 40, 25] },
  { cohort: 'Feb', data: [100, 55, 35] },
  { cohort: 'Mar', data: [100, 70] },
];
const generateHeatmapData = () => ({
  days: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
  times: ['08-10', '10-12', '12-14', '14-16', '16-18', '18-20'],
  matrix: [
    { day: 'Lun', time: '10-12', value: 70 }, { day: 'Lun', time: '12-14', value: 90 },
    { day: 'Mar', time: '12-14', value: 60 }, { day: 'Mié', time: '14-16', value: 85 },
    { day: 'Jue', time: '18-20', value: 50 }, { day: 'Vie', time: '10-12', value: 100 },
    { day: 'Sáb', time: '12-14', value: 75 },
  ]
});
const generateRadarData = () => [
  { label: 'Orgánico', value: 60 }, { label: 'Ads', value: 80 },
  { label: 'Redes', value: 45 }, { label: 'Email', value: 70 }, { label: 'Directo', value: 55 },
];

// ─── WIDGET LIBRARY ───────────────────────────────────────────────────────────
const WIDGET_LIBRARY = [
  { type: 'sparkline',  title: 'KPI con Tendencia',    icon: <Activity size={16} />,       defaultColSpan: 1, color: '#ef4444' },
  { type: 'waterfall',  title: 'Cascada (P&L)',         icon: <ArrowDownToLine size={16}/>, defaultColSpan: 2, color: '#10b981' },
  { type: 'funnel',     title: 'Embudo de Ventas',      icon: <ListFilter size={16} />,    defaultColSpan: 2, color: '#3b82f6' },
  { type: 'cohort',     title: 'Retención (Cohortes)',  icon: <Users size={16} />,         defaultColSpan: 2, color: '#6366f1' },
  { type: 'heatmap',    title: 'Mapa de Actividad',     icon: <CalendarDays size={16} />,  defaultColSpan: 2, color: '#10b981' },
  { type: 'radar',      title: 'Radar Omnicanal',       icon: <Radar size={16} />,         defaultColSpan: 2, color: '#8b5cf6' },
  { type: 'bar',        title: 'Ventas por Periodo',    icon: <BarChart3 size={16} />,     defaultColSpan: 2, color: '#3b82f6' },
  { type: 'horizontal', title: 'Top Productos',         icon: <AlignLeft size={16} />,     defaultColSpan: 2, color: '#475569' },
  { type: 'stacked',    title: 'Desglose Mensual',      icon: <BarChart2 size={16} />,     defaultColSpan: 2, color: '#7c3aed' },
  { type: 'area',       title: 'Volumen Acumulado',     icon: <Layers size={16} />,        defaultColSpan: 2, color: '#6366f1' },
  { type: 'doughnut',   title: 'Mix de Categorías',     icon: <CircleDashed size={16} />,  defaultColSpan: 2, color: '#f59e0b' },
  { type: 'line',       title: 'Línea de Tiempo',       icon: <LineChart size={16} />,     defaultColSpan: 2, color: '#10b981' },
  { type: 'pie',        title: 'Gráfico Circular',      icon: <PieChart size={16} />,      defaultColSpan: 2, color: '#3b82f6' },
  { type: 'kpi',        title: 'Métrica Simple',        icon: <Target size={16} />,        defaultColSpan: 1, color: '#ef4444' },
  { type: 'table',      title: 'Libro de Transacciones',icon: <TableIcon size={16} />,     defaultColSpan: 2, color: '#64748b' },
];

// ─── FILTRO DE FECHAS ─────────────────────────────────────────────────────────
function DateFilterBar({ dateFilters, setDateFilters }) {
  const { mode, year, month, day, from, to } = dateFilters;
  const setMode = (m) => setDateFilters(f => ({ ...f, mode: m }));

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 8 }, (_, i) => currentYear - i);
  const months = [
    ['01','Enero'], ['02','Febrero'], ['03','Marzo'], ['04','Abril'],
    ['05','Mayo'], ['06','Junio'], ['07','Julio'], ['08','Agosto'],
    ['09','Septiembre'], ['10','Octubre'], ['11','Noviembre'], ['12','Diciembre']
  ];

  return (
    <div className={styles.filterBar}>
      {/* Selector de modo */}
      <div className={styles.filterModeGroup}>
        {[['año','Año'], ['mes','Mes'], ['dia','Día'], ['rango','Rango']].map(([m, label]) => (
          <button
            key={m}
            className={`${styles.filterModeBtn} ${mode === m ? styles.filterModeBtnActive : ''}`}
            onClick={() => setMode(m)}
          >{label}</button>
        ))}
      </div>

      {/* Inputs según modo */}
      <div className={styles.filterInputsGroup}>
        {mode === 'año' && (
          <select
            className={styles.filterInput}
            value={year}
            onChange={e => setDateFilters(f => ({ ...f, year: e.target.value }))}
          >
            {years.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        )}

        {mode === 'mes' && (
          <>
            <select
              className={styles.filterInput}
              value={month}
              onChange={e => setDateFilters(f => ({ ...f, month: e.target.value }))}
            >
              {months.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
            <select
              className={styles.filterInput}
              style={{ maxWidth: 90 }}
              value={year}
              onChange={e => setDateFilters(f => ({ ...f, year: e.target.value }))}
            >
              {years.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </>
        )}

        {mode === 'dia' && (
          <input
            type="date"
            className={styles.filterInput}
            value={day}
            onChange={e => setDateFilters(f => ({ ...f, day: e.target.value }))}
          />
        )}

        {mode === 'rango' && (
          <>
            <input
              type="date"
              className={styles.filterInput}
              value={from}
              onChange={e => setDateFilters(f => ({ ...f, from: e.target.value }))}
            />
            <span className={styles.filterSep}>—</span>
            <input
              type="date"
              className={styles.filterInput}
              value={to}
              min={from}
              onChange={e => setDateFilters(f => ({ ...f, to: e.target.value }))}
            />
          </>
        )}
      </div>

      {/* Canal */}
      <select className={styles.filterChannelSelect}
        defaultValue="">
        <option value="">Todos los canales</option>
        <option value="online">Tienda Online</option>
        <option value="pos">Punto de Venta</option>
      </select>
    </div>
  );
}

// ─── EDITABLE TITLE ───────────────────────────────────────────────────────────
function EditableTitle({ title, onSave, isMain = false }) {
  const [isEditing, setIsEditing] = useState(false);
  const [val, setVal] = useState(title);
  if (isEditing) return (
    <div className={styles.editableTitleForm}>
      <input
        autoFocus
        className={styles.editableInput}
        style={{ fontSize: isMain ? '1.2rem' : '0.92rem' }}
        value={val}
        onChange={e => setVal(e.target.value)}
        onBlur={() => { onSave(val); setIsEditing(false); }}
        onKeyDown={e => { if (e.key === 'Enter') { onSave(val); setIsEditing(false); } }}
      />
    </div>
  );
  return (
    <div className={styles.editableTitleView} onClick={() => setIsEditing(true)}>
      {isMain
        ? <h2>{title}</h2>
        : <h3 className={styles.blockTitle}>{title}</h3>
      }
      <Edit2 size={13} className={styles.editIcon} />
    </div>
  );
}

// ─── CONTEXTO DE BLOQUE (métrica + agrupación) ────────────────────────────────
function BlockContext({ config, metadata }) {
  if (!config || !metadata) return null;
  const model  = metadata.modelos?.find(m => m.id === config.modelo);
  const metrica = model?.metricas?.find(m => m.id === config.metrica);
  const grupo   = model?.agrupaciones?.find(a => a.id === config.agrupar_por);
  if (!metrica && !grupo) return null;
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '0.5rem',
      flexWrap: 'wrap', marginBottom: '0.5rem',
      fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: 1.4
    }}>
      {model && (
        <span style={{
          background: 'rgba(var(--primary-rgb),0.08)', color: 'var(--primary)',
          padding: '2px 7px', borderRadius: 5, fontWeight: 700
        }}>{model.nombre}</span>
      )}
      {metrica && (
        <span style={{
          background: 'rgba(16,185,129,0.1)', color: '#059669',
          padding: '2px 7px', borderRadius: 5, fontWeight: 600
        }}>Mide: {metrica.nombre}</span>
      )}
      {grupo && (
        <span style={{
          background: 'rgba(245,158,11,0.1)', color: '#d97706',
          padding: '2px 7px', borderRadius: 5, fontWeight: 600
        }}>Por: {grupo.nombre}</span>
      )}
    </div>
  );
}

// ─── ESTADÍSTICAS DEL BLOQUE ──────────────────────────────────────────────────
function BlockStats({ data, type }) {
  if (!data || !data.length) return null;
  // No aplica a todos los tipos
  if (['heatmap', 'cohort'].includes(type)) return null;

  // Obtener valores numéricos
  const values = data
    .map(d => Number(d.resultado ?? d.value ?? 0))
    .filter(v => !isNaN(v) && v !== 0);

  if (!values.length) return null;

  const total = values.reduce((a, b) => a + b, 0);
  const avg   = total / values.length;
  const max   = Math.max(...values);
  const count = data.length;

  const fmt = (n) => {
    if (n >= 1_000_000) return `${(n/1_000_000).toFixed(1)}M`;
    if (n >= 1_000)     return `${(n/1_000).toFixed(1)}K`;
    return n.toLocaleString(undefined, { maximumFractionDigits: 1 });
  };

  const stat = (label, value, col = 'var(--text-muted)') => (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
      <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</span>
      <span style={{ fontSize: '0.88rem', fontWeight: 800, color: col, marginTop: '1px' }}>{value}</span>
    </div>
  );

  return (
    <div style={{
      display: 'flex', alignItems: 'stretch',
      borderTop: '1px solid var(--border-color)',
      marginTop: '0.75rem', paddingTop: '0.6rem',
      gap: '0', flexShrink: 0
    }}>
      {stat('Total', fmt(total), 'var(--primary)')}
      <div style={{ width: '1px', background: 'var(--border-color)' }} />
      {stat('Promedio', fmt(avg))}
      <div style={{ width: '1px', background: 'var(--border-color)' }} />
      {stat('Máximo', fmt(max))}
      <div style={{ width: '1px', background: 'var(--border-color)' }} />
      {stat('Registros', count)}
    </div>
  );
}

// ─── ESTADO VACÍO (widget sin configurar) ─────────────────────────────────────
function BlockEmpty({ type, onConfigure }) {
  const hints = {
    bar:       'Ventas agrupadas por periodo de tiempo',
    line:      'Evolución de una métrica a lo largo del tiempo',
    pie:       'Distribución porcentual por categoría',
    doughnut:  'Mix de ventas o cualquier proporción',
    sparkline: 'Un KPI clave con su tendencia',
    kpi:       'Un valor agregado único (suma, conteo)',
    waterfall: 'Ingresos menos costos — resultado neto',
    funnel:    'Tasa de conversión en el embudo de ventas',
    cohort:    'Retención de clientes mes a mes',
    heatmap:   'Intensidad de ventas por día y hora',
    radar:     'Comparación multidimensional de métricas',
    horizontal:'Ranking de productos, vendedores o categorías',
    stacked:   'Comparación de segmentos por periodo',
    area:      'Volumen acumulado con tendencia visual',
    table:     'Detalle fila a fila de transacciones',
  };
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      height: '100%', minHeight: '140px', gap: '0.6rem', padding: '1rem',
      background: 'rgba(var(--primary-rgb),0.02)', borderRadius: 10,
      border: '1.5px dashed rgba(var(--primary-rgb),0.2)', cursor: 'pointer'
    }} onClick={onConfigure}>
      <div style={{
        fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center',
        maxWidth: 220, lineHeight: 1.5, fontStyle: 'italic'
      }}>
        {hints[type] || 'Conecta datos para visualizar este widget'}
      </div>
      <button style={{
        display: 'flex', alignItems: 'center', gap: '0.35rem',
        padding: '0.4rem 1rem', background: 'var(--primary)', color: 'white',
        border: 'none', borderRadius: 7, fontWeight: 700, fontSize: '0.78rem',
        cursor: 'pointer', boxShadow: '0 2px 8px rgba(var(--primary-rgb),0.25)'
      }}>
        <Settings size={12} /> Conectar datos
      </button>
    </div>
  );
}

// ─── DASHBOARD BUILDER ────────────────────────────────────────────────────────
export default function DashboardBuilder() {
  const [reportName, setReportName] = useState('Dashboard de Ventas');
  const [blocks, setBlocks] = useState([]);
  const [draggedItemIndex, setDraggedItemIndex] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [loadingMeta, setLoadingMeta] = useState(true);
  const [configModalOpen, setConfigModalOpen] = useState(false);
  const [activeBlockId, setActiveBlockId] = useState(null);
  const [isExportMenuOpen, setIsExportMenuOpen] = useState(false);

  const currentYear = new Date().getFullYear();
  const currentMonth = String(new Date().getMonth() + 1).padStart(2, '0');
  const today = new Date().toISOString().split('T')[0];

  const [dateFilters, setDateFilters] = useState({
    mode: 'mes',
    year: String(currentYear),
    month: currentMonth,
    day: today,
    from: `${currentYear}-01-01`,
    to: today,
  });

  const MACROS = [
    { id: 'm1', name: 'Vista General de Ventas', blocks: [
      { id: 'b1', type: 'sparkline', title: 'Ticket Promedio', colSpan: 1 },
      { id: 'b2', type: 'bar', title: 'Ventas por Mes', colSpan: 2 },
      { id: 'b3', type: 'doughnut', title: 'Mix por Categoría', colSpan: 2 },
      { id: 'b4', type: 'table', title: 'Últimas Transacciones', colSpan: 2 },
    ]},
    { id: 'm2', name: 'Análisis de Clientes', blocks: [
      { id: 'b5', type: 'funnel', title: 'Embudo de Checkout', colSpan: 2 },
      { id: 'b6', type: 'cohort', title: 'Retención Mensual', colSpan: 2 },
      { id: 'b7', type: 'heatmap', title: 'Horas Pico de Ventas', colSpan: 2 },
    ]},
  ];

  useEffect(() => {
    api.get('reportes/metadata/')
      .then(r => setMetadata(r.data))
      .catch(console.error)
      .finally(() => setLoadingMeta(false));
  }, []);

  // Construir payload de fechas para la API según el modo activo
  const buildDatePayload = () => {
    const { mode, year, month, day, from, to } = dateFilters;
    if (mode === 'año')   return { fecha_desde: `${year}-01-01`, fecha_hasta: `${year}-12-31` };
    if (mode === 'mes')   return { fecha_desde: `${year}-${month}-01`, fecha_hasta: `${year}-${month}-31` };
    if (mode === 'dia')   return { fecha_desde: day, fecha_hasta: day };
    if (mode === 'rango') return { fecha_desde: from, fecha_hasta: to };
    return {};
  };

  const fetchBlockData = async (blockId, config) => {
    setBlocks(prev => prev.map(b => b.id === blockId ? { ...b, isLoading: true, error: null } : b));
    try {
      const payload = { ...config, ...buildDatePayload() };
      const r = await api.post('reportes/builder/', payload);
      setBlocks(prev => prev.map(b => b.id === blockId ? { ...b, data: r.data, isLoading: false, config } : b));
    } catch (err) {
      setBlocks(prev => prev.map(b => b.id === blockId ? {
        ...b, isLoading: false,
        error: err.response?.data?.error || 'Error al cargar datos'
      } : b));
    }
  };

  const handleSaveConfig = (config) => {
    const block = blocks.find(b => b.id === activeBlockId);
    if (block) fetchBlockData(block.id, config);
    setConfigModalOpen(false);
  };

  // ── Drag & Drop ───────────────────────────────────────────────
  const handleDragStartLibrary = (e, widget) => {
    const { icon, ...data } = widget;
    e.dataTransfer.setData('new-widget', JSON.stringify(data));
  };
  const handleDragStartCanvas = (e, index) => {
    setDraggedItemIndex(index);
    e.dataTransfer.setData('move-widget-index', index.toString());
    setTimeout(() => { e.target.style.opacity = '0.4'; }, 0);
  };
  const handleDragEndCanvas = (e) => { e.target.style.opacity = '1'; setDraggedItemIndex(null); };
  const handleDragOver = (e) => e.preventDefault();

  const spawnBlock = (template, insertAt = null) => {
    const nb = { id: `block-${Date.now()}`, type: template.type, title: template.title, colSpan: template.defaultColSpan, data: null, config: null };
    if (insertAt === null) setBlocks(prev => [...prev, nb]);
    else setBlocks(prev => { const a = [...prev]; a.splice(insertAt + 1, 0, nb); return a; });
    setActiveBlockId(nb.id);
    setConfigModalOpen(true);
    return nb;
  };

  const handleDropCanvas = (e) => {
    e.preventDefault();
    const raw = e.dataTransfer.getData('new-widget');
    if (raw) spawnBlock(JSON.parse(raw));
  };

  const handleDropBlock = (e, dropIndex) => {
    e.preventDefault(); e.stopPropagation();
    const moveStr = e.dataTransfer.getData('move-widget-index');
    if (moveStr !== '') {
      const di = parseInt(moveStr);
      if (di === dropIndex) return;
      setBlocks(prev => { const a = [...prev]; const [item] = a.splice(di, 1); a.splice(dropIndex, 0, item); return a; });
      return;
    }
    const raw = e.dataTransfer.getData('new-widget');
    if (raw) spawnBlock(JSON.parse(raw), dropIndex);
  };

  const removeBlock = (id) => setBlocks(b => b.filter(x => x.id !== id));
  const updateBlockTitle = (id, t) => setBlocks(b => b.map(x => x.id === id ? { ...x, title: t } : x));
  const changeBlockSize = (id, inc) => setBlocks(b => b.map(x => x.id === id ? { ...x, colSpan: Math.max(1, Math.min(2, x.colSpan + inc)) } : x));
  const loadMacro = (macro) => { setReportName(macro.name); setBlocks(macro.blocks.map(b => ({ ...b, id: `b-${Math.random()}` }))); };

  const renderWidgetContent = (block) => {
    const isMock = !block.data;

    // Resolver nombres de ejes desde metadata + config
    const model    = metadata?.modelos?.find(m => m.id === block.config?.modelo);
    const metricaMeta = model?.metricas?.find(m => m.id === block.config?.metrica);
    const grupoMeta   = model?.agrupaciones?.find(a => a.id === block.config?.agrupar_por);
    const yLabel = metricaMeta?.nombre || null;    // eje Y — qué se mide
    const xLabel = grupoMeta?.nombre   || null;    // eje X — cómo se agrupa

    switch (block.type) {
      case 'sparkline':  return <SparklineKPI title={block.title} value={isMock ? '$1,245' : (block.data[0]?.resultado || 0)} trend={isMock ? 12.5 : (block.data[0]?.trend || 0)} trendData={isMock ? [10,15,12,18,25,20,28] : block.data.map(d => d.resultado)} />;
      case 'waterfall':  return <CustomWaterfallChart data={isMock ? generateWaterfallData() : block.data} yLabel={yLabel} xLabel={xLabel} />;
      case 'cohort':     return <CustomCohortAnalysis data={isMock ? generateCohortData()    : block.data} />;
      case 'heatmap':    return <CustomHeatmap        data={isMock ? generateHeatmapData()   : block.data} />;
      case 'radar':      return <CustomRadarChart      data={isMock ? generateRadarData()     : block.data} />;
      case 'funnel':     return <CustomFunnelChart     data={isMock ? generateFunnelData()    : block.data} yLabel={yLabel} />;
      case 'stacked':    return <CustomStackedBarChart data={isMock ? generateStackedData()   : block.data} yLabel={yLabel} xLabel={xLabel} />;
      case 'bar':        return <CustomBarChart        data={isMock ? generateData()          : block.data} yLabel={yLabel} xLabel={xLabel} agruparPor={block.config?.agrupar_por} />;
      case 'horizontal': return <CustomHorizontalBarChart data={isMock ? generateData()      : block.data} yLabel={yLabel} xLabel={xLabel} />;
      case 'area':       return <CustomAreaChart       data={isMock ? generateData()          : block.data} yLabel={yLabel} xLabel={xLabel} agruparPor={block.config?.agrupar_por} />;
      case 'pie':        return <CustomPieChart        data={isMock ? generatePieData()       : block.data} />;
      case 'doughnut':   return <CustomDoughnutChart   data={isMock ? generatePieData()       : block.data} />;
      case 'line':       return <CustomLineChart       data={isMock ? generateData()          : block.data} yLabel={yLabel} xLabel={xLabel} agruparPor={block.config?.agrupar_por} />;
      case 'kpi':        return <KPICard title={block.title} data={isMock ? generateData()   : block.data} />;
      case 'table':      return <CustomTable data={isMock ? generateData()                    : block.data} columns={block.config?.select} xLabel={xLabel} yLabel={yLabel} />;
      default:           return <div className={styles.center} style={{ color: 'var(--text-muted)' }}>Widget no disponible</div>;
    }
  };

  if (loadingMeta) return <div className={styles.center} style={{ height: '80vh' }}><Spinner size="lg" /></div>;

  return (
    <div className={styles.dashboardContainer}>

      {/* HEADER */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.headerIcon}><LayoutDashboard size={18} /></div>
          <EditableTitle title={reportName} onSave={setReportName} isMain />
        </div>

        {/* FILTRO DE FECHAS CENTRAL */}
        <DateFilterBar dateFilters={dateFilters} setDateFilters={setDateFilters} />

        <div className={styles.headerRight}>
          {/* PLANTILLAS */}
          <div style={{ position: 'relative' }}>
            <button className={styles.btnOutline}>
              <FolderHeart size={15} style={{ color: '#ef4444' }} /> Plantillas
            </button>
            {/* Dropdown via CSS hover — simplificado */}
          </div>

          {/* EXPORTAR */}
          <div className={styles.exportDropdownContainer}>
            <button className={styles.btnPrimary} onClick={() => setIsExportMenuOpen(v => !v)}>
              <Download size={15} /> Exportar <ChevronDown size={13} />
            </button>
            {isExportMenuOpen && (
              <div className={styles.exportDropdown}>
                <button onClick={() => { setIsExportMenuOpen(false); generatePDF('dashboard', null, { blocks, title: reportName }); }}>
                  <FileText size={15} className={styles.iconRed} /> Documento PDF
                </button>
                <button onClick={() => { setIsExportMenuOpen(false); generateExcel('dashboard', null, { blocks, title: reportName }); }}>
                  <FileSpreadsheet size={15} className={styles.iconGreen} /> Archivo Excel
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* LAYOUT */}
      <div className={styles.mainLayout}>

        {/* SIDEBAR */}
        <aside className={styles.sidebar}>
          <div>
            <p className={styles.sidebarTitle}><Plus size={12} style={{ marginRight: 4 }} />Widgets ({WIDGET_LIBRARY.length})</p>
            <p className={styles.sidebarHelp}>Arrastra al canvas</p>
          </div>
          <div className={styles.widgetList}>
            {WIDGET_LIBRARY.map(w => (
              <div
                key={w.type}
                draggable
                onDragStart={e => handleDragStartLibrary(e, w)}
                className={styles.widgetItem}
              >
                <div className={styles.widgetIcon} style={{ color: w.color }}>{w.icon}</div>
                <span>{w.title}</span>
                <GripVertical size={13} className={styles.gripIcon} />
              </div>
            ))}
          </div>

          {/* MACROS */}
          <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem' }}>
            <p className={styles.sidebarTitle} style={{ marginBottom: '0.5rem' }}>Plantillas</p>
            {MACROS.map(m => (
              <button key={m.id} onClick={() => loadMacro(m)}
                style={{ width: '100%', textAlign: 'left', padding: '0.5rem 0.6rem', background: 'var(--bg-body)', border: '1px solid var(--border-color)', borderRadius: 7, marginBottom: '0.4rem', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}>
                {m.name}
                <span style={{ display: 'block', fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 400 }}>{m.blocks.length} widgets</span>
              </button>
            ))}
          </div>
        </aside>

        {/* CANVAS */}
        <main
          className={styles.canvas}
          onDragOver={handleDragOver}
          onDrop={handleDropCanvas}
        >
          {blocks.length === 0 ? (
            <div className={styles.emptyCanvas}>
              <div className={styles.emptyIcon}>
                <LayoutDashboard size={34} style={{ color: 'var(--primary)' }} />
              </div>
              <h3>Dashboard vacío</h3>
              <p>Arrastra widgets desde el panel izquierdo para comenzar a construir tu reporte</p>
            </div>
          ) : (
            <div className={styles.gridCanvas}>
              {blocks.map((block, index) => (
                <div
                  key={block.id}
                  draggable
                  onDragStart={e => handleDragStartCanvas(e, index)}
                  onDragEnd={handleDragEndCanvas}
                  onDragOver={handleDragOver}
                  onDrop={e => handleDropBlock(e, index)}
                  className={`${styles.blockCard} ${block.colSpan >= 2 ? styles.blockWide : ''}`}
                  style={{ opacity: draggedItemIndex === index ? 0.4 : 1 }}
                >
                  {/* Acciones */}
                  <div className={styles.blockOverlayActions}>
                    <button className={styles.actionBtnEdit}
                      onClick={() => { setActiveBlockId(block.id); setConfigModalOpen(true); }}>
                      <Settings size={11} /> {block.data ? 'Editar' : 'Conectar'}
                    </button>
                    <button className={styles.actionBtnEdit} onClick={() => changeBlockSize(block.id, -1)} disabled={block.colSpan <= 1} title="Reducir">
                      <Minimize2 size={11} />
                    </button>
                    <button className={styles.actionBtnEdit} onClick={() => changeBlockSize(block.id, 1)} disabled={block.colSpan >= 2} title="Ampliar">
                      <Maximize2 size={11} />
                    </button>
                    <button className={styles.actionBtnDrag} title="Mover"><GripVertical size={11} /></button>
                    <button className={styles.actionBtnDelete} onClick={() => removeBlock(block.id)} title="Eliminar">
                      <Trash2 size={11} />
                    </button>
                  </div>

                  {/* Cabecera */}
                  <div className={styles.blockHeader}>
                    <EditableTitle title={block.title} onSave={t => updateBlockTitle(block.id, t)} />
                    {block.data && (
                      <span style={{ fontSize: '0.65rem', background: 'rgba(16,185,129,0.12)', color: '#059669', padding: '2px 7px', borderRadius: 5, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', flexShrink: 0 }}>
                        {block.data.length} reg.
                      </span>
                    )}
                    {!block.data && !block.isLoading && (
                      <span style={{ fontSize: '0.65rem', background: 'rgba(245,158,11,0.15)', color: '#d97706', padding: '2px 7px', borderRadius: 5, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', flexShrink: 0 }}>Sin datos</span>
                    )}
                  </div>

                  {/* Contexto: qué modelo, métrica y agrupación */}
                  <BlockContext config={block.config} metadata={metadata} />

                  {/* Contenido */}
                  <div className={styles.blockContent}>
                    {block.isLoading && <div className={styles.center}><Spinner /></div>}
                    {block.error   && <div className={styles.blockError}>{block.error}</div>}
                    {!block.isLoading && !block.error && !block.data && (
                      <BlockEmpty type={block.type} onConfigure={() => { setActiveBlockId(block.id); setConfigModalOpen(true); }} />
                    )}
                    {!block.isLoading && !block.error && block.data && renderWidgetContent(block)}
                  </div>

                  {/* Estadísticas en el pie */}
                  {block.data && !block.isLoading && (
                    <BlockStats data={block.data} type={block.type} />
                  )}
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      {/* MODAL */}
      {configModalOpen && (
        <WidgetConfigModal
          metadata={metadata}
          block={blocks.find(b => b.id === activeBlockId)}
          onClose={() => setConfigModalOpen(false)}
          onSave={handleSaveConfig}
        />
      )}
    </div>
  );
}
