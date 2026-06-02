import { useState, useEffect } from 'react';
import { Database, Plus, History, Server, FileJson, X, RotateCcw, AlertTriangle, ChevronRight, Table } from 'lucide-react';
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
    const [successMsg, setSuccessMsg] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [backupName, setBackupName] = useState('Respaldo del Sistema');

    // Auto-Backup Config
    const [autoConfig, setAutoConfig] = useState({
        activo: false, frecuencia: 'DIARIO', hora_ejecucion: '00:00:00', dia_referencia: 0
    });
    const [savingConfig, setSavingConfig] = useState(false);

    // Restore
    const [restoring, setRestoring] = useState(false);
    const [isRestoreModalOpen, setIsRestoreModalOpen] = useState(false);
    const [restoreTargetBackup, setRestoreTargetBackup] = useState(null);

    // Explorer
    const [selectedBackup, setSelectedBackup] = useState(null);
    const [isExplorerOpen, setIsExplorerOpen] = useState(false);
    const [selectedSchema, setSelectedSchema] = useState('public');
    const [selectedTable, setSelectedTable] = useState('');
    const [searchTable, setSearchTable] = useState('');

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

    const fetchConfig = async () => {
        try {
            const res = await api.get('/respaldos/config/');
            setAutoConfig(res.data);
        } catch (err) {
            console.error('Error loading backup config', err);
        }
    };

    useEffect(() => {
        fetchBackups();
        fetchConfig();
    }, []);

    const saveConfig = async () => {
        setSavingConfig(true);
        try {
            await api.post('/respaldos/config/', autoConfig);
            setSuccessMsg('Configuración guardada correctamente');
            setTimeout(() => setSuccessMsg(null), 3000);
        } catch (err) {
            setError('Error guardando configuración');
        } finally {
            setSavingConfig(false);
        }
    };

    const openRestoreModal = (backup, e) => {
        if (e) e.stopPropagation();
        setRestoreTargetBackup(backup);
        setIsRestoreModalOpen(true);
    };

    const handleRestore = async () => {
        if (!restoreTargetBackup) return;
        setRestoring(true);
        setError(null);
        try {
            await api.post(`/respaldos/${restoreTargetBackup.id}/restaurar/`);
            setIsRestoreModalOpen(false);
            setIsExplorerOpen(false);
            setSuccessMsg('✅ Sistema restaurado con éxito. Recargando...');
            setTimeout(() => window.location.reload(), 2000);
        } catch (err) {
            setError('Error crítico al restaurar: ' + (err.response?.data?.error || err.message));
            setIsRestoreModalOpen(false);
        } finally {
            setRestoring(false);
        }
    };

    const handleCreate = async () => {
        setCreating(true);
        setError(null);
        try {
            await api.post('/respaldos/', { nombre: backupName });
            setIsModalOpen(false);
            setSuccessMsg('✅ Snapshot creado correctamente.');
            setTimeout(() => setSuccessMsg(null), 3000);
            fetchBackups();
        } catch (err) {
            setError('Error al crear el respaldo: ' + (err.response?.data?.error || err.message));
        } finally {
            setCreating(false);
        }
    };

    const openExplorer = (backup) => {
        const catalogo = backup.metadata?.catalogo || {};
        const schemas = Object.keys(catalogo);
        setSelectedBackup({ ...backup, catalogo, schemas });
        setSearchTable('');
        if (schemas.length > 0) {
            const firstSchema = schemas.includes('public') ? 'public' : schemas[0];
            setSelectedSchema(firstSchema);
            const tables = Object.keys(catalogo[firstSchema] || {});
            if (tables.length > 0) setSelectedTable(tables[0]);
        }
        setIsExplorerOpen(true);
    };

    const totalSize = backups.reduce((acc, b) => acc + (b.metadata?.size_bytes || 0), 0);

    // ─── Columnas de la tabla principal ────────────────────────────────────────
    const COLUMNS = [
        {
            key: 'nombre',
            label: 'Snapshot',
            render: (v, row) => (
                <div>
                    <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{v}</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>{row.fecha_display}</div>
                </div>
            )
        },
        {
            key: 'metadata',
            label: 'Tamaño',
            render: (m) => (
                <div style={{ fontSize: '13px' }}>
                    <strong>{m?.size_bytes ? `${(m.size_bytes / (1024 * 1024)).toFixed(2)} MB` : '—'}</strong>
                    <div style={{ color: 'var(--color-text-muted)', fontSize: '11px' }}>{m?.formato || 'Binary'}</div>
                </div>
            )
        },
        {
            key: 'archivo_path',
            label: 'Ruta',
            render: (v) => (
                <code style={{ fontSize: '10px', color: '#94a3b8', display: 'block', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={v}>
                    {v}
                </code>
            )
        },
        {
            key: 'id',
            label: 'Acciones',
            render: (id, row) => (
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <button
                        onClick={(e) => { e.stopPropagation(); openExplorer(row); }}
                        style={{
                            display: 'flex', alignItems: 'center', gap: '5px',
                            padding: '5px 10px', borderRadius: '6px', border: '1px solid #3b82f633',
                            background: 'rgba(59,130,246,0.08)', color: '#60a5fa',
                            cursor: 'pointer', fontSize: '12px', fontWeight: 'bold'
                        }}
                    >
                        <FileJson size={13} /> Explorar
                    </button>
                    <button
                        onClick={(e) => openRestoreModal(row, e)}
                        style={{
                            display: 'flex', alignItems: 'center', gap: '5px',
                            padding: '5px 10px', borderRadius: '6px', border: '1px solid #ef444433',
                            background: 'rgba(239,68,68,0.08)', color: '#f87171',
                            cursor: 'pointer', fontSize: '12px', fontWeight: 'bold'
                        }}
                    >
                        <RotateCcw size={13} /> Restaurar
                    </button>
                </div>
            )
        }
    ];

    // ─── Renderizar contenido del explorador ────────────────────────────────────
    const renderExplorerContent = () => {
        if (!selectedBackup?.catalogo) return null;

        const currentSchemaData = selectedBackup.catalogo[selectedSchema] || {};
        const tableInfo = currentSchemaData[selectedTable] || { columns: [], rows: [] };
        const allTables = Object.keys(currentSchemaData).filter(t =>
            !searchTable || t.toLowerCase().includes(searchTable.toLowerCase())
        );

        const totalRows = Object.values(currentSchemaData).reduce((acc, t) => acc + (t.count || 0), 0);

        return (
            <div style={{ display: 'flex', flex: 1, height: '100%', background: '#0f172a', color: '#f8fafc', overflow: 'hidden' }}>

                {/* ── Sidebar ── */}
                <div style={{ width: '260px', background: '#111827', borderRight: '1px solid #1e293b', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>

                    {/* Schema selector */}
                    <div style={{ padding: '16px', borderBottom: '1px solid #1e293b' }}>
                        <label style={{ fontSize: '10px', color: '#64748b', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '1px' }}>
                            Esquema / Tienda
                        </label>
                        <select
                            value={selectedSchema}
                            onChange={(e) => {
                                const s = e.target.value;
                                setSelectedSchema(s);
                                setSearchTable('');
                                const tables = Object.keys(selectedBackup.catalogo[s] || {});
                                setSelectedTable(tables[0] || '');
                            }}
                            style={{ width: '100%', marginTop: '8px', background: '#1f2937', color: 'white', border: '1px solid #374151', padding: '8px', borderRadius: '8px', outline: 'none' }}
                        >
                            {selectedBackup.schemas.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                        <div style={{ marginTop: '8px', fontSize: '11px', color: '#64748b' }}>
                            {Object.keys(currentSchemaData).length} tablas · {totalRows} filas capturadas
                        </div>
                    </div>

                    {/* Table search */}
                    <div style={{ padding: '12px 16px', borderBottom: '1px solid #1e293b' }}>
                        <input
                            placeholder="Buscar tabla..."
                            value={searchTable}
                            onChange={e => setSearchTable(e.target.value)}
                            style={{
                                width: '100%', background: '#1f2937', color: 'white', border: '1px solid #374151',
                                padding: '7px 10px', borderRadius: '6px', outline: 'none', fontSize: '12px', boxSizing: 'border-box'
                            }}
                        />
                    </div>

                    {/* Table list */}
                    <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
                        {allTables.length === 0 && (
                            <div style={{ padding: '20px', textAlign: 'center', color: '#4b5563', fontSize: '12px' }}>Sin tablas</div>
                        )}
                        {allTables.map(table => {
                            const count = currentSchemaData[table]?.count || 0;
                            const isActive = selectedTable === table;
                            return (
                                <div
                                    key={table}
                                    onClick={() => setSelectedTable(table)}
                                    style={{
                                        padding: '9px 12px', borderRadius: '7px', cursor: 'pointer',
                                        marginBottom: '3px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                        background: isActive ? 'rgba(59,130,246,0.15)' : 'transparent',
                                        color: isActive ? '#60a5fa' : '#9ca3af',
                                        border: `1px solid ${isActive ? '#3b82f633' : 'transparent'}`,
                                        transition: 'all 0.15s'
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                                        <Table size={13} style={{ flexShrink: 0 }} />
                                        <span style={{ fontSize: '12px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{table}</span>
                                    </div>
                                    <span style={{ fontSize: '10px', color: isActive ? '#93c5fd' : '#4b5563', flexShrink: 0, marginLeft: '4px' }}>
                                        {count}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* ── Data Viewer ── */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                    {/* Subheader */}
                    <div style={{ padding: '12px 20px', background: '#111827', borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <ChevronRight size={14} color="#64748b" />
                            <span style={{ color: '#64748b', fontSize: '12px' }}>{selectedSchema}</span>
                            <ChevronRight size={14} color="#64748b" />
                            <span style={{ color: 'white', fontWeight: 'bold', fontSize: '13px' }}>{selectedTable}</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <span style={{ fontSize: '11px', color: '#64748b' }}>
                                Mostrando {tableInfo.rows?.length || 0} filas (muestra)
                            </span>
                            <Badge variant="primary">{tableInfo.columns?.length || 0} columnas</Badge>
                        </div>
                    </div>

                    {/* Table data */}
                    <div style={{ flex: 1, overflow: 'auto' }}>
                        {tableInfo.columns && tableInfo.columns.length > 0 ? (
                            <table style={{ width: 'max-content', minWidth: '100%', borderCollapse: 'collapse' }}>
                                <thead style={{ position: 'sticky', top: 0, background: '#1e293b', zIndex: 5 }}>
                                    <tr>
                                        <th style={{ padding: '10px 14px', textAlign: 'left', color: '#64748b', fontSize: '10px', borderBottom: '1px solid #334155', textTransform: 'uppercase', whiteSpace: 'nowrap', fontWeight: 'bold' }}>
                                            #
                                        </th>
                                        {tableInfo.columns.map(col => (
                                            <th key={col} style={{
                                                padding: '10px 14px', textAlign: 'left', color: '#94a3b8', fontSize: '10px',
                                                borderBottom: '1px solid #334155', textTransform: 'uppercase', whiteSpace: 'nowrap', letterSpacing: '0.5px'
                                            }}>
                                                {col}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {tableInfo.rows.map((row, idx) => (
                                        <tr key={idx} style={{
                                            borderBottom: '1px solid #1e293b',
                                            background: idx % 2 === 0 ? '#0f172a' : '#0d1520'
                                        }}>
                                            <td style={{ padding: '8px 14px', color: '#475569', fontSize: '11px', whiteSpace: 'nowrap', userSelect: 'none' }}>
                                                {idx + 1}
                                            </td>
                                            {tableInfo.columns.map(col => {
                                                const val = row[col];
                                                const isNull = val === '' || val === null || val === undefined;
                                                const isNum = !isNaN(val) && val !== '' && typeof val !== 'boolean';
                                                return (
                                                    <td key={col} style={{
                                                        padding: '8px 14px', fontSize: '12px', whiteSpace: 'nowrap',
                                                        maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis',
                                                        color: isNull ? '#4b5563' : isNum ? '#a5f3fc' : '#d1d5db'
                                                    }} title={String(val)}>
                                                        {isNull ? <em style={{ color: '#4b5563' }}>null</em> : String(val)}
                                                    </td>
                                                );
                                            })}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#4b5563', gap: '15px' }}>
                                <History size={64} opacity={0.15} />
                                <div style={{ textAlign: 'center' }}>
                                    <p style={{ margin: 0, fontWeight: 'bold' }}>Tabla vacía o sin muestra</p>
                                    <p style={{ fontSize: '12px', marginTop: '6px' }}>
                                        {selectedTable
                                            ? 'Esta tabla no tenía datos en el momento del snapshot.'
                                            : 'Selecciona una tabla del panel izquierdo.'}
                                    </p>
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
            subtitle="Gestión de snapshots · Explorador de datos · Restauración del sistema"
        >
            {error && <Alert variant="danger" style={{ marginBottom: '16px' }}>{error}</Alert>}
            {successMsg && <Alert variant="success" style={{ marginBottom: '16px' }}>{successMsg}</Alert>}

            <StatCard.Group>
                <StatCard
                    label="Total Snapshots"
                    value={backups.length}
                    icon={<History size={18} />}
                />
                <StatCard
                    label="Almacenamiento Total"
                    value={totalSize > 0 ? `${(totalSize / (1024 * 1024)).toFixed(1)} MB` : '—'}
                    icon={<Server size={18} />}
                />
                <StatCard
                    label="Último Backup"
                    value={backups.length > 0 ? backups[backups.length - 1].fecha_display : '—'}
                    icon={<Database size={18} />}
                    accentColor="var(--color-success)"
                />
            </StatCard.Group>

            <div style={{ marginTop: '24px', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                    <DataTable
                        title="Historial de Snapshots"
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

                {/* Panel de Configuración Automática */}
                <div style={{ width: '300px', background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '20px', flexShrink: 0 }}>
                    <h3 style={{ margin: '0 0 15px 0', fontSize: '15px', color: 'var(--color-text)' }}>Respaldo Automático</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '14px', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={autoConfig.activo}
                                onChange={e => setAutoConfig({ ...autoConfig, activo: e.target.checked })}
                            />
                            Habilitar respaldos automáticos
                        </label>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                            <label style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Frecuencia</label>
                            <select
                                value={autoConfig.frecuencia}
                                onChange={e => setAutoConfig({ ...autoConfig, frecuencia: e.target.value })}
                                style={{
                                    padding: '8px 10px', borderRadius: '6px',
                                    border: '1px solid var(--color-border)',
                                    background: 'var(--color-surface)',
                                    color: 'var(--color-text)',
                                    fontSize: '14px', outline: 'none', width: '100%'
                                }}
                                disabled={!autoConfig.activo}
                            >
                                <option value="DIARIO">Diario</option>
                                <option value="SEMANAL">Semanal</option>
                                <option value="MENSUAL">Mensual</option>
                            </select>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                            <label style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Hora de ejecución</label>
                            <input
                                type="time"
                                value={autoConfig.hora_ejecucion}
                                onChange={e => setAutoConfig({ ...autoConfig, hora_ejecucion: e.target.value })}
                                style={{
                                    padding: '8px 10px', borderRadius: '6px',
                                    border: '1px solid var(--color-border)',
                                    background: 'var(--color-surface)',
                                    color: 'var(--color-text)',
                                    fontSize: '14px', outline: 'none', width: '100%', boxSizing: 'border-box'
                                }}
                                disabled={!autoConfig.activo}
                                step="1"
                            />
                        </div>

                        {autoConfig.frecuencia !== 'DIARIO' && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                                <label style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                                    {autoConfig.frecuencia === 'SEMANAL' ? 'Día de la semana (0=Lun, 6=Dom)' : 'Día del mes (1-31)'}
                                </label>
                                <input
                                    type="number" min={0} max={31}
                                    value={autoConfig.dia_referencia}
                                    onChange={e => setAutoConfig({ ...autoConfig, dia_referencia: parseInt(e.target.value) })}
                                    style={{
                                        padding: '8px 10px', borderRadius: '6px',
                                        border: '1px solid var(--color-border)',
                                        background: 'var(--color-surface)',
                                        color: 'var(--color-text)',
                                        fontSize: '14px', outline: 'none', width: '100%', boxSizing: 'border-box'
                                    }}
                                    disabled={!autoConfig.activo}
                                />
                            </div>
                        )}

                        <Button variant="primary" fullWidth onClick={saveConfig} loading={savingConfig}>
                            Guardar Configuración
                        </Button>
                    </div>
                </div>
            </div>

            {/* ── VISOR FULL SCREEN ── */}
            {isExplorerOpen && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
                    background: '#020617', zIndex: 9999, display: 'flex', flexDirection: 'column'
                }}>
                    {/* Header */}
                    <div style={{
                        padding: '14px 24px', background: '#0f172a', borderBottom: '1px solid #1e293b',
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0
                    }}>
                        <div>
                            <h2 style={{ margin: 0, fontSize: '17px', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <Database color="#60a5fa" size={20} />
                                Explorador: <span style={{ color: '#60a5fa' }}>{selectedBackup?.nombre}</span>
                            </h2>
                            <p style={{ margin: '3px 0 0', fontSize: '11px', color: '#64748b' }}>
                                {selectedBackup?.fecha_display} · Muestra de hasta 20 filas por tabla
                            </p>
                        </div>
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <Button
                                variant="danger"
                                onClick={() => openRestoreModal(selectedBackup)}
                                style={{ display: 'flex', alignItems: 'center', gap: '7px' }}
                            >
                                <RotateCcw size={15} /> Restaurar este Snapshot
                            </Button>
                            <button
                                onClick={() => setIsExplorerOpen(false)}
                                style={{
                                    cursor: 'pointer', padding: '9px 14px', borderRadius: '8px',
                                    display: 'flex', alignItems: 'center', gap: '7px',
                                    background: '#1e293b', border: '1px solid #334155', color: '#94a3b8',
                                    transition: 'all 0.2s', fontSize: '13px'
                                }}
                                onMouseOver={e => { e.currentTarget.style.background = '#334155'; e.currentTarget.style.color = 'white'; }}
                                onMouseOut={e => { e.currentTarget.style.background = '#1e293b'; e.currentTarget.style.color = '#94a3b8'; }}
                            >
                                <X size={16} /> Cerrar
                            </button>
                        </div>
                    </div>

                    {/* Content */}
                    <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                        {renderExplorerContent()}
                    </div>
                </div>
            )}

            {/* ── MODAL CREAR SNAPSHOT ── */}
            <Modal
                isOpen={isModalOpen}
                onClose={() => !creating && setIsModalOpen(false)}
                title="Nuevo Snapshot del Sistema"
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setIsModalOpen(false)} disabled={creating}>Cancelar</Button>
                        <Button onClick={handleCreate} disabled={creating}>
                            {creating ? <Spinner size="sm" /> : 'Confirmar Snapshot'}
                        </Button>
                    </>
                }
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', margin: 0 }}>
                        Se generará un punto de restauración binario con copia exacta de toda la base de datos (todos los esquemas y tenants incluidos).
                    </p>
                    <Input
                        label="Nombre del punto de restauración"
                        value={backupName}
                        onChange={e => setBackupName(e.target.value)}
                    />
                </div>
            </Modal>

            {/* ── MODAL RESTAURACIÓN — z-index por encima del visor ── */}
            <Modal
                isOpen={isRestoreModalOpen}
                onClose={() => !restoring && setIsRestoreModalOpen(false)}
                title="⚠️ Confirmar Restauración"
                zIndex={99999}
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setIsRestoreModalOpen(false)} disabled={restoring}>
                            Cancelar
                        </Button>
                        <Button variant="danger" onClick={handleRestore} loading={restoring}>
                            {restoring ? <><Spinner size="sm" /> Restaurando...</> : 'Sí, Restaurar Sistema'}
                        </Button>
                    </>
                }
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div style={{
                        display: 'flex', alignItems: 'flex-start', gap: '14px',
                        padding: '16px', borderRadius: '10px', background: 'rgba(239,68,68,0.08)',
                        border: '1px solid rgba(239,68,68,0.3)'
                    }}>
                        <AlertTriangle size={24} color="#f87171" style={{ flexShrink: 0, marginTop: '2px' }} />
                        <div>
                            <p style={{ margin: 0, fontWeight: 'bold', color: '#f87171', fontSize: '14px' }}>
                                Esta acción es irreversible
                            </p>
                            <p style={{ margin: '6px 0 0', fontSize: '13px', color: 'var(--color-text-muted)' }}>
                                Todos los datos creados o modificados <strong>después</strong> de este snapshot se perderán permanentemente.
                            </p>
                        </div>
                    </div>
                    <div style={{ padding: '14px', borderRadius: '10px', background: 'var(--color-bg-muted)', border: '1px solid var(--color-border)' }}>
                        <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Restaurando snapshot:</div>
                        <div style={{ fontWeight: 'bold', fontSize: '16px', marginTop: '4px' }}>{restoreTargetBackup?.nombre}</div>
                        <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '2px' }}>{restoreTargetBackup?.fecha_display}</div>
                    </div>
                    <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: 0 }}>
                        El sistema quedará inaccesible durante el proceso. Al finalizar se recargará automáticamente.
                    </p>
                </div>
            </Modal>
        </AppView>
    );
}
