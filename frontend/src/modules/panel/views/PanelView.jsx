import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, TrendingUp, Package, AlertTriangle } from 'lucide-react';
import AppView   from 'shared/widgets/AppView/AppView';
import StatCard  from 'shared/widgets/StatCard/StatCard';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Button, Badge, Alert } from 'shared/components';
import { useTenant } from 'core/hooks/useTenant';
import { restockApi } from 'modules/tienda/services/restockApi';
import api from 'core/services/api';

// ─── Columnas de la tabla de productos ───────────────────────
const COLUMNS = [
  { key: 'nombre',      label: 'Producto',    render: (v) => <strong style={{ color: 'var(--color-text)' }}>{v}</strong> },
  { key: 'descripcion', label: 'Descripción', render: (v) => v || '—' },
  { key: 'precio',      label: 'Precio',      render: (v) => `BS. ${parseFloat(v).toLocaleString()}` },
  { key: 'stock',       label: 'Stock',       align: 'center', render: (v) => `${v} un.` },
  {
    key: 'stock_estado',
    label: 'Estado',
    align: 'center',
    render: (_, row) => (
      <Badge variant={row.stock < 10 ? 'warning' : 'success'} dot>
        {row.stock < 10 ? 'Bajo Stock' : 'Disponible'}
      </Badge>
    ),
  },
];

// ─── Columnas de la tabla de Intención de Compra (Restock) ───
const RESTOCK_COLUMNS = [
  { key: 'producto', label: 'Producto', render: (v) => <strong style={{ color: 'var(--color-text)' }}>{v}</strong> },
  { key: 'cantidad_solicitudes', label: 'Solicitudes', align: 'center', render: (v) => (
      <Badge variant="warning" dot>{v}</Badge>
  ) },
  { key: 'ultima_solicitud', label: 'Última solicitud', align: 'center', render: (v) => (
      v ? new Date(v).toLocaleDateString() : '—'
  ) },
];

const MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];

// ─── Card de ventas por mes ───────────────────────────────────
function SalesMonthCard({ facturas }) {
  const ahora = new Date();
  const anio  = ahora.getFullYear();

  // Agrupar montos por mes del año actual
  const porMes = Array(12).fill(0);
  facturas.forEach((f) => {
    if (!f.fecha) return;
    const [y, m] = f.fecha.split('-').map(Number);
    if (y === anio) porMes[m - 1] += parseFloat(f.monto_total || 0);
  });

  const maxVal = Math.max(...porMes, 1);
  const totalAnio = porMes.reduce((a, b) => a + b, 0);
  const mesActualIdx = ahora.getMonth();
  const mesActualMonto = porMes[mesActualIdx];
  const pctMesActual = totalAnio > 0 ? ((mesActualMonto / totalAnio) * 100).toFixed(1) : 0;

  return (
    <div style={{
      background: 'var(--color-surface)',
      border: '1px solid var(--color-border)',
      borderRadius: 'var(--radius-lg, 12px)',
      padding: '20px 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ margin: 0, fontSize: 12, color: 'var(--color-text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Ventas por Mes
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 26, fontWeight: 700, color: 'var(--color-text)', lineHeight: 1 }}>
            {pctMesActual}%
          </p>
          <p style={{ margin: '4px 0 0', fontSize: 11, color: 'var(--color-text-muted)' }}>
            del total anual en {MESES[mesActualIdx]}
          </p>
        </div>
        <div style={{
          width: 36, height: 36, borderRadius: '50%',
          background: 'var(--color-primary, #6366f1)20',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--color-primary, #6366f1)',
        }}>
          <TrendingUp size={16} />
        </div>
      </div>

      {/* Mini bar chart */}
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 52, marginTop: 4 }}>
        {porMes.map((val, i) => {
          const pct = maxVal > 0 ? (val / maxVal) * 100 : 0;
          const esMesActual = i === mesActualIdx;
          return (
            <div
              key={i}
              title={`${MESES[i]}: BS. ${val.toLocaleString()}`}
              style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}
            >
              <div style={{
                width: '100%',
                height: `${Math.max(pct, 4)}%`,
                background: esMesActual
                  ? 'var(--color-primary, #6366f1)'
                  : 'var(--color-primary, #6366f1)40',
                borderRadius: '3px 3px 0 0',
                transition: 'height 0.4s ease',
                minHeight: 3,
              }} />
              <span style={{
                fontSize: 9,
                color: esMesActual ? 'var(--color-primary, #6366f1)' : 'var(--color-text-muted)',
                fontWeight: esMesActual ? 700 : 400,
              }}>
                {MESES[i]}
              </span>
            </div>
          );
        })}
      </div>

      {/* Footer total */}
      <p style={{ margin: 0, fontSize: 11, color: 'var(--color-text-muted)', borderTop: '1px solid var(--color-border)', paddingTop: 10 }}>
        Total {anio}: <strong style={{ color: 'var(--color-text)' }}>BS. {totalAnio.toLocaleString()}</strong>
        &nbsp;·&nbsp;{facturas.length} factura{facturas.length !== 1 ? 's' : ''}
      </p>
    </div>
  );
}

export default function PanelView() {
  const tenant = useTenant();
  const navigate = useNavigate();
  const [products,  setProducts]  = useState([]);
  const [facturas,  setFacturas]  = useState([]);
  const [restock,   setRestock]   = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [resProd, resFact, resRestock] = await Promise.all([
          api.get('/productos/'),
          api.get('/facturas/'),
          restockApi.ranking().catch(() => ({ data: [] })),
        ]);
        const prodData = resProd.data;
        const factData = resFact.data;
        const restockData = resRestock.data;
        setProducts(Array.isArray(prodData) ? prodData : Array.isArray(prodData?.results) ? prodData.results : []);
        setFacturas(Array.isArray(factData) ? factData : Array.isArray(factData?.results) ? factData.results : []);
        setRestock(Array.isArray(restockData) ? restockData : Array.isArray(restockData?.results) ? restockData.results : []);
        setError(null);
      } catch {
        setError('No se pudo conectar con el servidor.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [tenant]);

  const valorTotal  = products.reduce((acc, p) => acc + parseFloat(p.precio || 0) * (p.stock || 0), 0);
  const stockBajo   = products.filter((p) => p.stock < 10).length;

  return (
    <AppView
      title={`Bienvenido, ${tenant}`}
      subtitle="Resumen del inventario y actividad de tu tienda."
      actions={
        <Button leftIcon={<Plus size={16} />} onClick={() => navigate('/productos')}>
          Nuevo Producto
        </Button>
      }
    >
      {error && <Alert variant="danger">{error}</Alert>}

      {/* KPI Cards */}
      <StatCard.Group>
        <StatCard
          label="Valor del Inventario"
          value={`BS. ${valorTotal.toLocaleString()}`}
          change="Calculado en tiempo real"
          trend="neutral"
          icon={<TrendingUp size={18} />}
        />
        <StatCard
          label="Productos Activos"
          value={products.length}
          change="Sincronizado con API"
          trend="positive"
          icon={<Package size={18} />}
          accentColor="var(--color-accent)"
        />
        <StatCard
          label="Stock Crítico"
          value={stockBajo}
          change={stockBajo > 0 ? 'Requieren atención' : 'Todo en orden'}
          trend={stockBajo > 0 ? 'negative' : 'positive'}
          icon={<AlertTriangle size={18} />}
          accentColor={stockBajo > 0 ? 'var(--color-warning)' : 'var(--color-success)'}
        />
      </StatCard.Group>

      {/* Card de ventas por mes */}
      <SalesMonthCard facturas={facturas} />

      {/* Tabla de productos */}
      <DataTable
        title="Inventario de Base de Datos"
        columns={COLUMNS}
        data={products}
        loading={loading}
        emptyText="No hay productos registrados para este tenant."
        footer={!loading ? `Mostrando ${products.length} producto${products.length !== 1 ? 's' : ''}` : ''}
      />

      {/* Intención de Compra (Restock) */}
      <DataTable
        title="Intención de Compra"
        columns={RESTOCK_COLUMNS}
        data={restock}
        loading={loading}
        emptyText="Aún no hay solicitudes de aviso de stock."
        footer={!loading && restock.length ? `${restock.length} producto${restock.length !== 1 ? 's' : ''} con demanda` : ''}
      />
    </AppView>
  );
}
