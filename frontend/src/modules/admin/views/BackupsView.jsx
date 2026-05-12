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
    const [selectedSchema, setSelectedSchema] = useState('public');
    const [selectedTable, setSelectedTable] = useState('');

    const openExplorer = (backup) => {
        const catalogo = backup.metadata?.catalogo || {};
        const schemas = Object.keys(catalogo);
        setSelectedBackup({ ...backup, catalogo, schemas });
        
        if (schemas.length > 0) {
            const firstSchema = schemas.includes('public') ? 'public' : schemas[0];
            setSelectedSchema(firstSchema);
            const tables = Object.keys(catalogo[firstSchema] || {});
            if (tables.length > 0) setSelectedTable(tables[0]);
        }
        setIsExplorerOpen(true);
    };

    const COLUMNS = [
        { 
            key: 'fecha_display', 
            label: 'Versión', 
            render: (v, row) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Badge variant="primary" size="lg" style={{ minWidth: '100px', textAlign: 'center' }}>{v}</Badge>
                    <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={(e) => { e.stopPropagation(); openExplorer(row); }}
                        style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-primary)', border: '1px solid #e0e7ff' }}
                    >
                        <FileJson size={14} />
                        <span style={{ fontSize: '11px', fontWeight: 'bold' }}>Explorar</span>
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
            key: 'archivo_path', 
            label: 'Ruta Servidor', 
            render: (v) => <code style={{fontSize: '10px', color: '#94a3b8', display: 'block', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis'}} title={v}>{v}</code> 
        }
    ];

    const renderExplorerContent = () => {
        if (!selectedBackup || !selectedBackup.catalogo) return null;
        
        const currentSchemaData = selectedBackup.catalogo[selectedSchema] || {};
        const tableInfo = currentSchemaData[selectedTable] || { columns: [], rows: [] };
        const allTables = Object.keys(currentSchemaData);

        return (
            <div style={{ 
                display: 'flex', 
                height: '70vh', 
                background: '#0f172a', 
                borderRadius: '12px', 
                overflow: 'hidden',
                border: '1px solid #1e293b'
            }}>
                {/* Sidebar Izquierda */}
                <div style={{ 
                    width: '280px', 
                    background: '#111827', 
                    borderRight: '1px solid #1e293b',
                    display: 'flex',
                    flexDirection: 'column'
                }}>
                    <div style={{ padding: '20px', borderBottom: '1px solid #1e293b' }}>
                        <label style={{ fontSize: '11px', color: '#64748b', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '1px' }}>Esquema / Tienda</label>
                        <select 
                            value={selectedSchema}
                            onChange={(e) => {
                                const newSchema = e.target.value;
                                setSelectedSchema(newSchema);
                                const firstTable = Object.keys(selectedBackup.catalogo[newSchema] || {})[0];
                                setSelectedTable(firstTable || '');
                            }}
                            style={{ 
                                width: '100%', marginTop: '10px', background: '#1f2937', color: 'white', 
                                border: '1px solid #374151', padding: '10px', borderRadius: '8px', outline: 'none' 
                            }}
                        >
                            {selectedBackup.schemas.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                    </div>

                    <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
                        <label style={{ fontSize: '11px', color: '#64748b', fontWeight: 'bold', padding: '10px', display: 'block' }}>TABLAS DETECTADAS</label>
                        {allTables.map(table => (
                            <div 
                                key={table}
                                onClick={() => setSelectedTable(table)}
                                style={{ 
                                    padding: '10px 15px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px',
                                    marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '10px',
                                    background: selectedTable === table ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                                    color: selectedTable === table ? '#60a5fa' : '#9ca3af',
                                    border: `1px solid ${selectedTable === table ? '#3b82f633' : 'transparent'}`,
                                    transition: 'all 0.2s'
                                }}
                            >
                                <Database size={14} />
                                {table}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Visor de Datos Derecha */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#0f172a' }}>
                    <div style={{ padding: '15px 25px', background: '#111827', borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <span style={{ color: '#64748b', fontSize: '12px' }}>Viendo tabla: </span>
                            <span style={{ color: 'white', fontWeight: 'bold' }}>{selectedSchema}.{selectedTable}</span>
                        </div>
                        <Badge variant="primary">{tableInfo.rows?.length || 0} filas en muestra</Badge>
                    </div>

                    <div style={{ flex: 1, overflow: 'auto' }}>
                        {tableInfo.columns && tableInfo.columns.length > 0 ? (
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead style={{ position: 'sticky', top: 0, background: '#1f2937', zIndex: 10 }}>
                                    <tr>
                                        {tableInfo.columns.map(col => (
                                            <th key={col} style={{ padding: '12px 15px', textAlign: 'left', color: '#9ca3af', fontSize: '11px', borderBottom: '1px solid #374151', textTransform: 'uppercase' }}>{col}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {tableInfo.rows.map((row, idx) => (
                                        <tr key={idx} style={{ borderBottom: '1px solid #1e293b', background: idx % 2 === 0 ? '#0f172a' : '#111827' }}>
                                            {tableInfo.columns.map(col => (
                                                <td key={col} style={{ padding: '10px 15px', color: '#d1d5db', fontSize: '12px', whiteSpace: 'nowrap' }}>
                                                    {String(row[col])}
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#4b5563', gap: '15px' }}>
                                <History size={64} opacity={0.2} />
                                <div style={{ textAlign: 'center' }}>
                                    <p style={{ margin: 0, fontWeight: 'bold' }}>Sin datos disponibles</p>
                                    <p style={{ fontSize: '12px' }}>Crea un backup nuevo para ver el contenido real de esta tabla.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );
    };

    return (
        <AppView 
            title="Copias de Seguridad" 
            subtitle="Gestión de snapshots con explorador de catálogo Premium"
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
                    label="Almacenamiento" 
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

            <Modal
                isOpen={isExplorerOpen}
                onClose={() => setIsExplorerOpen(false)}
                title={`Explorador de Datos: ${selectedBackup?.nombre}`}
                width="95vw"
            >
                {renderExplorerContent()}
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
                        Se generará un punto de restauración binario con catálogo de datos reales (Vista Previa).
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
