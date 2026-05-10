import { useState, useEffect } from 'react';
import { Shield, Activity, Users, FileText } from 'lucide-react';
import AppView   from 'shared/widgets/AppView/AppView';
import StatCard  from 'shared/widgets/StatCard/StatCard';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Badge, Alert } from 'shared/components';
import { useTenant } from 'core/hooks/useTenant';
import api from 'core/services/api';

const COLUMNS = [
  { key: 'fecha', label: 'Fecha/Hora', render: (v) => new Date(v).toLocaleString() },
  { key: 'usuario_nombre', label: 'Usuario', render: (v, row) => `${v || 'Desconocido'} (${row.usuario_email || ''})` },
  { key: 'accion', label: 'Acción', render: (v) => <Badge variant={v === 'LOGIN' ? 'success' : v === 'LOGOUT' ? 'warning' : 'primary'}>{v}</Badge> },
  { key: 'modulo', label: 'Módulo' },
  { key: 'metadatos', label: 'Metadatos', render: (v) => v ? JSON.stringify(v) : '—' }
];

export default function AdminView() {
  const tenant = useTenant();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await api.get('/bitacora/');
        const data = res.data;
        const list = Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : [];
        setLogs(list);
        setError(null);
      } catch (err) {
        console.error(err);
        setError('No se pudo cargar la bitácora de actividad.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [tenant]);

  const logins = logs.filter(l => l.accion === 'LOGIN').length;
  const hoy = logs.filter(l => new Date(l.fecha).toDateString() === new Date().toDateString()).length;

  return (
    <AppView
      title="Panel de Administrador"
      subtitle="Auditoría del sistema y bitácora de actividades"
    >
      {error && <Alert variant="danger">{error}</Alert>}

      <StatCard.Group>
        <StatCard
          label="Total de Registros"
          value={logs.length}
          change="Histórico completo"
          trend="neutral"
          icon={<Activity size={18} />}
        />
        <StatCard
          label="Inicios de Sesión"
          value={logins}
          change="Accesos registrados"
          trend="positive"
          icon={<Users size={18} />}
          accentColor="var(--color-success)"
        />
        <StatCard
          label="Actividad Hoy"
          value={hoy}
          change="Eventos de hoy"
          trend={hoy > 0 ? 'positive' : 'neutral'}
          icon={<FileText size={18} />}
          accentColor="var(--color-primary)"
        />
      </StatCard.Group>

      <DataTable
        title="Bitácora de Actividades"
        columns={COLUMNS}
        data={logs}
        loading={loading}
        emptyText="No hay registros en la bitácora."
        footer={!loading ? `Mostrando ${logs.length} registro${logs.length !== 1 ? 's' : ''}` : ''}
      />
    </AppView>
  );
}
