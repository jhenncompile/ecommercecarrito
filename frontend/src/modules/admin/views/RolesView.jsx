import { useState, useEffect } from 'react';
import { Users, Plus, Edit, Trash2, CheckCircle, ShieldCheck } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Button, Input, Badge, Alert, Modal } from 'shared/components';
import api from 'core/services/api';

export default function RolesView() {
    const [roles, setRoles] = useState([]);
    const [permisos, setPermisos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [formData, setFormData] = useState({ nombre: '', descripcion: '', nivel: 4, permisos: [] });
    const [editingId, setEditingId] = useState(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [rolesRes, permisosRes] = await Promise.all([
                api.get('/roles/'),
                api.get('/permisos/')
            ]);
            setRoles(rolesRes.data.results || rolesRes.data);
            setPermisos(permisosRes.data.results || permisosRes.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchData(); }, []);

    const togglePermission = (permId) => {
        const current = formData.permisos || [];
        if (current.includes(permId)) {
            setFormData({ ...formData, permisos: current.filter(id => id !== permId) });
        } else {
            setFormData({ ...formData, permisos: [...current, permId] });
        }
    };

    const handleSave = async () => {
        try {
            if (editingId) {
                await api.put(`/roles/${editingId}/`, formData);
            } else {
                await api.post('/roles/', formData);
            }
            setIsModalOpen(false);
            fetchData();
        } catch (err) {
            alert('Error al guardar el rol');
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Eliminar este rol?')) return;
        try {
            await api.delete(`/roles/${id}/`);
            fetchData();
        } catch (err) {
            alert('No se pudo eliminar el rol');
        }
    };

    const COLUMNS = [
        { key: 'nombre', label: 'Nombre' },
        { key: 'descripcion', label: 'Descripción' },
        { 
            key: 'nivel', label: 'Nivel', 
            render: (v) => <Badge variant={v === 1 ? 'primary' : 'secondary'}>{v === 1 ? 'ADMIN' : v === 2 ? 'VENDEDOR' : 'CLIENTE'}</Badge> 
        },
        { 
            key: 'permisos_detalles', label: 'Permisos', 
            render: (perms) => (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {perms?.map(p => <Badge key={p.id} variant="outline" size="sm">{p.codigo}</Badge>)}
                    {!perms?.length && <span style={{ color: 'var(--color-text-muted)', fontSize: '12px' }}>Ninguno</span>}
                </div>
            )
        },
        {
            key: 'id', label: 'Acciones', align: 'right',
            render: (id, row) => (
                <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                    <Button variant="ghost" size="sm" onClick={() => {
                        setEditingId(id);
                        setFormData({
                            nombre: row.nombre,
                            descripcion: row.descripcion,
                            nivel: row.nivel,
                            permisos: row.permisos || []
                        });
                        setIsModalOpen(true);
                    }}>
                        <Edit size={14} />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(id)}>
                        <Trash2 size={14} color="var(--color-danger)" />
                    </Button>
                </div>
            )
        }
    ];

    return (
        <AppView title="Gestionar Roles" subtitle="Define niveles de acceso y responsabilidades">
            
            <DataTable
                title="Lista de Roles"
                columns={COLUMNS}
                data={roles}
                loading={loading}
                actions={
                    <Button onClick={() => { setEditingId(null); setFormData({ nombre: '', descripcion: '', nivel: 4, permisos: [] }); setIsModalOpen(true); }}>
                        <Plus size={18} style={{ marginRight: '8px' }} /> Nuevo Rol
                    </Button>
                }
            />

            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={editingId ? "Editar Rol" : "Nuevo Rol"}
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
                        <Button onClick={handleSave}>Guardar Rol</Button>
                    </>
                }
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <Input label="Nombre del Rol" value={formData.nombre} onChange={e => setFormData({...formData, nombre: e.target.value})} />
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Nivel de Acceso</label>
                            <select 
                                value={formData.nivel} 
                                onChange={e => setFormData({...formData, nivel: parseInt(e.target.value)})}
                                style={{ padding: '8px', borderRadius: '8px', border: '1px solid var(--color-border)' }}
                            >
                                <option value={1}>Admin (Nivel 1)</option>
                                <option value={2}>Vendedor (Nivel 2)</option>
                                <option value={3}>Cliente (Nivel 3)</option>
                                <option value={4}>Invitado (Nivel 4)</option>
                            </select>
                        </div>
                    </div>
                    <Input label="Descripción" value={formData.descripcion} onChange={e => setFormData({...formData, descripcion: e.target.value})} multiline />
                    
                    <div>
                        <label style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', display: 'block' }}>Asignar Permisos</label>
                        <div style={{ 
                            display: 'grid', 
                            gridTemplateColumns: '1fr 1fr', 
                            gap: '10px', 
                            maxHeight: '200px', 
                            overflowY: 'auto',
                            padding: '10px',
                            border: '1px solid var(--color-border)',
                            borderRadius: '8px'
                        }}>
                            {permisos.map(p => (
                                <div 
                                    key={p.id} 
                                    onClick={() => togglePermission(p.id)}
                                    style={{ 
                                        display: 'flex', 
                                        alignItems: 'center', 
                                        gap: '8px', 
                                        cursor: 'pointer',
                                        padding: '4px 8px',
                                        borderRadius: '6px',
                                        background: formData.permisos.includes(p.id) ? 'var(--color-primary-light, #eef2ff)' : 'transparent'
                                    }}
                                >
                                    {formData.permisos.includes(p.id) ? <ShieldCheck size={16} color="var(--color-primary)" /> : <div style={{width: 16, height: 16, border: '1px solid #ccc', borderRadius: '4px'}} />}
                                    <span style={{ fontSize: '12px' }}>{p.nombre}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </Modal>
        </AppView>
    );
}
