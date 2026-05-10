import { useState, useEffect } from 'react';
import { Database, Download, Plus, ArrowRight, History, Server, FileJson } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import StatCard from 'shared/widgets/StatCard/StatCard';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Button, Badge, Alert, Modal, Input, Spinner } from 'shared/components';
import api from 'core/services/api';

export default function BackupsView() {
    const [backups, setBackups] = useState([]);
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [backupName, setBackupName] = useState('Respaldo del Sistema');

    const fetchBackups = async () => {
        setLoading(true);
        try {
            const res = await api.get('/respaldos/historial/');
            setBackups(res.data);
            setError(null);
        } catch (err) {
            setError('Error al cargar historial de respaldos.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchBackups(); }, []);

    const handleCreate = async () => {
        setCreating(true);
        try {
            await api.post('/respaldos/', { nombre: backupName });
            setIsModalOpen(false);
            fetchBackups();
        } catch (err) {
            setError('Error al crear el respaldo en el servidor.');
        } finally {
            setCreating(false);
        }
    };

    const COLUMNS = [
        { 
            key: 'fecha_display', 
            label: 'Versión', 
            render: (v) => <Badge variant="primary" size="lg">{v}</Badge> 
        },
        { key: 'nombre', label: 'Identificador' },
        { 
            key: 'anterior_id', 
            label: 'Cola (Anterior)', 
            render: (v) => v ? <span>v. {backups.find(b => b.id === v)?.fecha_display || v}</span> : <Badge variant="outline">Raíz</Badge> 
        },
        { 
            key: 'siguiente_id', 
            label: 'Siguiente', 
            render: (v) => v ? <span>v. {backups.find(b => b.id === v)?.fecha_display || v}</span> : <Badge variant="success">Actual ✨</Badge> 
        },
        { 
            key: 'metadata', 
            label: 'Tamaño', 
            render: (m) => m?.size_bytes ? `${(m.size_bytes / (1024 * 1024)).toFixed(2)} MB` : '—' 
        },
        { 
            key: 'archivo_path', 
            label: 'Ruta Servidor', 
            render: (v) => <code style={{fontSize: '10px', color: 'var(--color-text-muted)'}}>{v}</code> 
        }
    ];

    return (
        <AppView 
            title="Copias de Seguridad" 
            subtitle="Gestión de backups con versionado encadenado"
        >
            {error && <Alert variant="danger">{error}</Alert>}

            <StatCard.Group>
                <StatCard 
                    label="Versión Actual" 
                    value={backups.length > 0 ? `v. ${backups[backups.length - 1].fecha_display}` : '—'}
                    icon={<Database size={18} />}
                />
                <StatCard 
                    label="Total Versiones" 
                    value={backups.length}
                    icon={<History size={18} />}
                />
                <StatCard 
                    label="Ubicación Servidor" 
                    value="/backups"
                    icon={<Server size={18} />}
                    accentColor="var(--color-warning)"
                />
            </StatCard.Group>

            <div style={{ marginTop: '24px' }}>
                <DataTable
                    title="Historial de Versiones"
                    columns={COLUMNS}
                    data={backups}
                    loading={loading}
                    actions={
                        <Button onClick={() => setIsModalOpen(true)}>
                            <Plus size={18} style={{ marginRight: '8px' }} /> Generar Backup
                        </Button>
                    }
                />
            </div>

            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title="Nuevo Respaldo del Sistema"
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
                        <Button onClick={handleCreate} disabled={creating}>
                            {creating ? <Spinner size="sm" /> : 'Confirmar Backup'}
                        </Button>
                    </>
                }
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <p style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>
                        Se realizará un volcado de la base de datos (PostgreSQL) y se almacenará en el servidor. 
                        La nueva versión se enlazará automáticamente con la versión anterior.
                    </p>
                    <Input 
                        label="Nombre descriptivo" 
                        value={backupName} 
                        onChange={e => setBackupName(e.target.value)} 
                    />
                </div>
            </Modal>
        </AppView>
    );
}
