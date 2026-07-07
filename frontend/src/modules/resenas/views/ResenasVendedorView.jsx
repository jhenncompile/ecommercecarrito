import { useState, useEffect } from 'react';
import { Star, MessageSquare, Package } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import StatCard from 'shared/widgets/StatCard/StatCard';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Alert } from 'shared/components';
import { useTenant } from 'core/hooks/useTenant';
import { resenasApi } from 'modules/tienda/services/resenasApi';

const STAR_COLOR = '#f59e0b';

// ─── Estrellas ────────────────────────────────────────────────
function Estrellas({ valor, size = 15 }) {
  return (
    <span style={{ display: 'inline-flex', gap: '2px' }}>
      {[0, 1, 2, 3, 4].map((i) => (
        <Star key={i} size={size} color={STAR_COLOR} fill={valor >= i + 1 ? STAR_COLOR : 'none'} />
      ))}
    </span>
  );
}

// ─── Columnas de la tabla de reseñas ──────────────────────────
const COLUMNS = [
  { key: 'producto_nombre', label: 'Producto', render: (v) => <strong style={{ color: 'var(--color-text)' }}>{v || '—'}</strong> },
  { key: 'cliente_nombre', label: 'Cliente', render: (v) => v || '—' },
  { key: 'calificacion', label: 'Calificación', align: 'center', render: (v) => <Estrellas valor={Number(v) || 0} /> },
  { key: 'comentario', label: 'Comentario', render: (v) => v || <span style={{ color: 'var(--color-text-muted)' }}>Sin comentario</span> },
  { key: 'created_at', label: 'Fecha', align: 'center', render: (v) => (v ? new Date(v).toLocaleDateString() : '—') },
];

export default function ResenasVendedorView() {
  const { tenant } = useTenant();
  const [resenas, setResenas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError('');
      try {
        const res = await resenasApi.listar();
        const data = Array.isArray(res.data) ? res.data : (res.data?.results || []);
        if (active) setResenas(data);
      } catch {
        if (active) setError('No se pudieron cargar las reseñas.');
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [tenant]);

  const total = resenas.length;
  const promedio = total ? resenas.reduce((a, r) => a + (Number(r.calificacion) || 0), 0) / total : 0;
  const productosResenados = new Set(resenas.map((r) => r.producto_nombre)).size;

  return (
    <AppView
      title="Reseñas y Calificaciones"
      subtitle="Opiniones de tus compradores sobre los productos de tu tienda."
    >
      {error && <Alert variant="danger">{error}</Alert>}

      <StatCard.Group>
        <StatCard
          label="Total de Reseñas"
          value={total}
          change="En toda la tienda"
          trend="neutral"
          icon={<MessageSquare size={18} />}
        />
        <StatCard
          label="Calificación Promedio"
          value={`${promedio.toFixed(1)} / 5`}
          change={total ? 'Promedio general' : 'Sin datos aún'}
          trend={promedio >= 4 ? 'positive' : promedio > 0 ? 'neutral' : 'negative'}
          icon={<Star size={18} />}
          accentColor={STAR_COLOR}
        />
        <StatCard
          label="Productos Reseñados"
          value={productosResenados}
          change="Con al menos una reseña"
          trend="positive"
          icon={<Package size={18} />}
          accentColor="var(--color-accent)"
        />
      </StatCard.Group>

      <DataTable
        title="Todas las Reseñas"
        columns={COLUMNS}
        data={resenas}
        loading={loading}
        emptyText="Aún no hay reseñas de tus productos."
        footer={!loading && total ? `${total} reseña${total !== 1 ? 's' : ''}` : ''}
      />
    </AppView>
  );
}
