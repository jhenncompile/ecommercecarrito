import { useState, useEffect } from 'react';
import { Store, Globe, Server, CheckCircle } from 'lucide-react';
import AppView   from 'shared/widgets/AppView/AppView';
import StatCard  from 'shared/widgets/StatCard/StatCard';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Badge, Alert } from 'shared/components';
import api from 'core/services/api';

const COLUMNS = [
  { key: 'nombre_comercial', label: 'Nombre de la Tienda', render: (v, row) => <strong style={{ color: 'var(--color-text)' }}>{v || row.name || 'Sin Nombre'}</strong> },
  { key: 'schema_name', label: 'Esquema', render: (v) => <Badge variant="primary">{v}</Badge> },
  { key: 'subdominio', label: 'Dominio/Subdominio', render: (v) => v ? <a href={`http://${v}`} target="_blank" rel="noreferrer" style={{ color: 'var(--color-primary)' }}>{v}</a> : '—' },
  { key: 'estado', label: 'Estado', align: 'center', render: () => <Badge variant="success" dot>Activo</Badge> }
];

export default function AdminTiendasView() {
  const [tiendas, setTiendas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await api.get('/tiendas/');
        const data = res.data;
        const list = Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : [];
        setTiendas(list);
        setError(null);
      } catch (err) {
        console.error(err);
        setError('No se pudo cargar la lista de tiendas.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const total = tiendas.length;
  const conDominio = tiendas.filter(t => t.dominio && !t.dominio.includes('localhost') && !t.dominio.includes('nip.io')).length;

  return (
    <AppView
      title="Gestión de Tiendas (Tenants)"
      subtitle="Supervisa todas las tiendas y dominios registrados en la plataforma"
    >
      {error && <Alert variant="danger">{error}</Alert>}

      <StatCard.Group>
        <StatCard
          label="Total de Tiendas"
          value={total}
          change="Instancias activas"
          trend="positive"
          icon={<Store size={18} />}
          accentColor="var(--color-success)"
        />
        <StatCard
          label="Dominios Personalizados"
          value={conDominio}
          change="Configurados en prod"
          trend={conDominio > 0 ? 'positive' : 'neutral'}
          icon={<Globe size={18} />}
          accentColor="var(--color-primary)"
        />
        <StatCard
          label="Estado del Sistema"
          value="Operativo"
          change="Conectado a la BD Central"
          trend="positive"
          icon={<Server size={18} />}
        />
      </StatCard.Group>

      <DataTable
        title="Tiendas Registradas"
        columns={COLUMNS}
        data={tiendas}
        loading={loading}
        emptyText="No hay tiendas registradas en el sistema."
        footer={!loading ? `Mostrando ${tiendas.length} tienda${tiendas.length !== 1 ? 's' : ''}` : ''}
      />
    </AppView>
  );
}
