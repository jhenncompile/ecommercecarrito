import { useState, useEffect } from 'react';
import { Key, Plus, Edit, Trash2, Search } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Button, Input, Badge, Alert, Modal } from 'shared/components';
import api from 'core/services/api';

export default function PermisosView() {
    const [permisos, setPermisos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [formData, setFormData] = useState({ nombre: '', codigo: '', descripcion: '', modulo: '' });
    const [editingId, setEditingId] = useState(null);

    const fetchPermisos = async () => {
        setLoading(true);
        try {
            const res = await api.get('/permisos/');
            setPermisos(res.data.results || res.data);
        } catch (err) {
            setError('Error al cargar permisos.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchPermisos(); }, []);

    const handleSave = async () => {
        try {
            if (editingId) {
                await api.put(`/permisos/${editingId}/`, formData);
            } else {
                await api.post('/permisos/', formData);
            }
            setIsModalOpen(false);
            setFormData({ nombre: '', codigo: '', descripcion: '', modulo: '' });
            setEditingId(null);
            fetchPermisos();
        } catch (err) {
            alert('Error al guardar el permiso');
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Eliminar este permiso?')) return;
        try {
            await api.delete(`/permisos/${id}/`);
            fetchPermisos();
        } catch (err) {
            alert('No se pudo eliminar el permiso');
        }
    };

    const COLUMNS = [
        { key: 'nombre', label: 'Nombre' },
        { key: 'codigo', label: 'Código', render: (v) => <Badge variant="secondary">{v}</Badge> },
        { key: 'modulo', label: 'Módulo' },
        { key: 'descripcion', label: 'Descripción' },
        {
            key: 'id', label: 'Acciones', align: 'right',
            render: (id, row) => (
                <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                    <Button variant="ghost" size="sm" onClick={() => {
                        setEditingId(id);
                        setFormData(row);
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
        <AppView title="Gestionar Permisos" subtitle="Acciones y accesos del sistema">
            {error && <Alert variant="danger">{error}</Alert>}
            
            <DataTable
                title="Lista de Permisos"
                columns={COLUMNS}
                data={permisos}
                loading={loading}
                actions={
                    <Button onClick={() => { setEditingId(null); setFormData({ nombre: '', codigo: '', descripcion: '', modulo: '' }); setIsModalOpen(true); }}>
                        <Plus size={18} style={{ marginRight: '8px' }} /> Nuevo Permiso
                    </Button>
                }
            />

            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={editingId ? "Editar Permiso" : "Nuevo Permiso"}
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
                        <Button onClick={handleSave}>Guardar</Button>
                    </>
                }
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <Input label="Nombre del Permiso" value={formData.nombre} onChange={e => setFormData({...formData, nombre: e.target.value})} placeholder="Ej: Crear Productos" />
                    <Input label="Código Único" value={formData.codigo} onChange={e => setFormData({...formData, codigo: e.target.value.toUpperCase()})} placeholder="Ej: PRODUCTOS_CREAR" />
                    <Input label="Módulo" value={formData.modulo} onChange={e => setFormData({...formData, modulo: e.target.value})} placeholder="Ej: Inventario" />
                    <Input label="Descripción" value={formData.descripcion} onChange={e => setFormData({...formData, descripcion: e.target.value})} multiline />
                </div>
            </Modal>
        </AppView>
    );
}
