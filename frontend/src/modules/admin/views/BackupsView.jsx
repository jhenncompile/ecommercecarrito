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

    const [selectedBackup, setSelectedBackup] = useState(null);
    const [isExplorerOpen, setIsExplorerOpen] = useState(false);

    const openExplorer = (backup) => {
        setSelectedBackup(backup);
        setIsExplorerOpen(true);
    };

    const COLUMNS = [
        { 
            key: 'fecha_display', 
            label: 'Versión', 
            render: (v, row) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Badge variant="primary" size="lg" style={{ minWidth: '60px', textAlign: 'center' }}>{v}</Badge>
                    <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={(e) => { e.stopPropagation(); openExplorer(row); }}
                        style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-primary)', border: '1px solid #e0e7ff' }}
                    >
                        <FileJson size={14} />
                        <span style={{ fontSize: '11px', fontWeight: 'bold' }}>Explorar Catálogo</span>
                    </Button>
                </div>
            )
        },
        { key: 'nombre', label: 'Identificador' },
        { 
            key: 'metadata', 
            label: 'Info', 
            render: (m) => (
                <div style={{ fontSize: '12px' }}>
                    <div><strong>{m?.size_bytes ? `${(m.size_bytes / (1024 * 1024)).toFixed(2)} MB` : '—'}</strong></div>
                    <div style={{ color: 'var(--color-text-muted)' }}>{m?.formato || 'SQL Plano'}</div>
                </div>
            )
        },
        { 
            key: 'anterior_id', 
            label: 'Origen', 
            render: (v) => v ? <span style={{fontSize: '12px'}}>v. {backups.find(b => b.id === v)?.fecha_display || v}</span> : <Badge variant="outline">Raíz</Badge> 
        },
        { 
            key: 'siguiente_id', 
            label: 'Estado', 
            render: (v) => v ? <span style={{fontSize: '12px', color: 'var(--color-text-muted)'}}>Sucedido</span> : <Badge variant="success">Actual ✨</Badge> 
        },
        { 
            key: 'archivo_path', 
            label: 'Ruta Servidor', 
            render: (v) => <code style={{fontSize: '10px', color: 'var(--color-text-muted)', display: 'block', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis'}} title={v}>{v}</code> 
        }
    ];

    return (
        <AppView 
            title="Copias de Seguridad" 
            subtitle="Gestión de snapshots con explorador de catálogo"
        >
            {error && <Alert variant="danger" style={{ marginBottom: '20px' }}>{error}</Alert>}

            <StatCard.Group>
                <StatCard 
                    label="Versión Actual" 
                    value={backups.length > 0 ? `v. ${backups[backups.length - 1].fecha_display}` : '—'}
                    icon={<Database size={18} />}
                />
                <StatCard 
                    label="Puntos de Restauración" 
                    value={backups.length}
                    icon={<History size={18} />}
                />
                <StatCard 
                    label="Estado de Almacenamiento" 
                    value="Optimizado"
                    icon={<Server size={18} />}
                    accentColor="var(--color-success)"
                />
            </StatCard.Group>

            <div style={{ marginTop: '24px' }}>
                <DataTable
                    title="Cronología de Versiones"
                    columns={COLUMNS}
                    data={backups}
                    loading={loading}
                    onRowClick={openExplorer}
                    actions={
                        <Button onClick={() => setIsModalOpen(true)}>
                            <Plus size={18} style={{ marginRight: '8px' }} /> Crear Snapshot
                        </Button>
                    }
                />
            </div>

            {/* MODAL EXPLORADOR DE BACKUP */}
            <Modal
                isOpen={isExplorerOpen}
                onClose={() => setIsExplorerOpen(false)}
                title={`Explorador de Snapshot: ${selectedBackup?.nombre} (v. ${selectedBackup?.fecha_display})`}
                size="lg"
            >
                <div style={{ minHeight: '300px' }}>
                    {selectedBackup?.metadata?.catalogo ? (
                        <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr', gap: '20px' }}>
                            <div style={{ borderRight: '1px solid var(--color-border)', paddingRight: '15px' }}>
                                <h4 style={{ fontSize: '14px', marginBottom: '12px', color: 'var(--color-primary)' }}>Esquemas / Tiendas</h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                    {Object.entries(selectedBackup.metadata.catalogo).map(([schema, info]) => (
                                        <div key={schema} style={{ padding: '8px', borderRadius: '6px', background: '#f8fafc', fontSize: '13px' }}>
                                            <div style={{ fontWeight: '600' }}>{schema}</div>
                                            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>{info.total_tablas} tablas registradas</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <h4 style={{ fontSize: '14px', marginBottom: '12px' }}>Vista previa de estructura</h4>
                                <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginBottom: '15px' }}>
                                    Este snapshot binario contiene la estructura completa del sistema. A continuación se muestran algunas tablas clave detectadas:
                                </p>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                    {selectedBackup.metadata.catalogo['public']?.tablas?.map(t => (
                                        <Badge key={t} variant="outline" size="sm">{t}</Badge>
                                    ))}
                                    {Object.keys(selectedBackup.metadata.catalogo).length > 1 && <Badge variant="primary" size="sm">+ Datos de Tiendas</Badge>}
                                </div>
                                <div style={{ marginTop: '30px', padding: '20px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px' }}>
                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <Download size={24} style={{ color: '#d97706' }} />
                                        <div>
                                            <h5 style={{ margin: 0, fontSize: '14px' }}>Formato Restaurable</h5>
                                            <p style={{ margin: '5px 0 0', fontSize: '12px' }}>
                                                Este archivo .dump puede ser restaurado íntegramente usando la utilidad <code>pg_restore</code>.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div style={{ textAlign: 'center', padding: '40px' }}>
                            <FileJson size={48} style={{ color: 'var(--color-text-muted)', marginBottom: '15px' }} />
                            <p>Esta versión es antigua y no contiene un catálogo interactivo.</p>
                        </div>
                    )}
                </div>
            </Modal>

            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title="Nuevo Snapshot del Sistema"
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
                        <Button onClick={handleCreate} disabled={creating}>
                            {creating ? <Spinner size="sm" /> : 'Confirmar Snapshot'}
                        </Button>
                    </>
                }
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <p style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>
                        Se generará un punto de restauración binario optimizado con compresión máxima y catálogo de metadatos.
                    </p>
                    <Input 
                        label="Nombre del punto de restauración" 
                        value={backupName} 
                        onChange={e => setBackupName(e.target.value)} 
                    />
                </div>
            </Modal>
        </AppView>
    );
}
