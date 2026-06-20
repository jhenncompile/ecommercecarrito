import { useState, useEffect } from 'react';
import { Users, Plus, Edit, Trash2, Shield, Mail, CheckCircle, XCircle } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Button, Input, Badge, Modal } from 'shared/components';
import api from 'core/services/api';
import { isBaseDomain } from 'core/utils/domain';

export default function UsersView() {
    const [users, setUsers] = useState([]);
    const [roles, setRoles] = useState([]);
    const [tenants, setTenants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [isPublic, setIsPublic] = useState(false);
    const [currentUserEmail, setCurrentUserEmail] = useState(null);
    const [currentUserIsAdmin, setCurrentUserIsAdmin] = useState(false);

    const [formData, setFormData] = useState({
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        is_active: true,
        is_staff: false,
        is_superuser: false,
        tenant: '',
        roles: []
    });

    const fetchData = async () => {
        setLoading(true);
        try {
            // Detectar si estamos en el dominio público
            const hostname = window.location.hostname;
            const publicMode = isBaseDomain(hostname);
            setIsPublic(publicMode);

            const requests = [
                api.get('/usuarios/'),
                api.get('/roles/'),
                api.get('/usuarios/perfil/') // Para saber quién soy yo
            ];

            if (publicMode) {
                requests.push(api.get('/tiendas/'));
            }

            const [usersRes, rolesRes, profileRes, tenantsRes] = await Promise.all(requests);
            
            setUsers(usersRes.data.results || usersRes.data);
            setRoles(rolesRes.data.results || rolesRes.data);
            setCurrentUserEmail(profileRes.data.email);
            setCurrentUserIsAdmin(profileRes.data.is_staff || profileRes.data.is_superuser);
            if (tenantsRes) {
                setTenants(tenantsRes.data.results || tenantsRes.data);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchData(); }, []);

    const handleSave = async () => {
        // Validación de contraseña fuerte
        if (!editingId || formData.password) {
            const pass = formData.password;
            const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
            
            if (pass.length < 8) {
                alert('La contraseña debe tener al menos 8 caracteres');
                return;
            }
            if (!strongPasswordRegex.test(pass)) {
                alert('Seguridad insuficiente: La contraseña debe incluir Mayúsculas, Minúsculas, Números y un Carácter Especial (@$!%*?&)');
                return;
            }
        }

        try {
            const dataToSave = { ...formData };
            if (editingId && !dataToSave.password) {
                delete dataToSave.password;
            }
            if (!dataToSave.tenant) dataToSave.tenant = null;

            if (editingId) {
                await api.put(`/usuarios/${editingId}/`, dataToSave);
            } else {
                await api.post('/usuarios/', dataToSave);
            }
            setIsModalOpen(false);
            fetchData();
        } catch (err) {
            const errorMsg = err.response?.data?.password?.[0] || 'Error al guardar el usuario';
            alert(errorMsg);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Eliminar este usuario?')) return;
        try {
            await api.delete(`/usuarios/${id}/`);
            fetchData();
        } catch (err) {
            alert('No se pudo eliminar el usuario');
        }
    };

    const toggleRole = (roleId) => {
        const current = formData.roles || [];
        if (current.includes(roleId)) {
            setFormData({ ...formData, roles: current.filter(id => id !== roleId) });
        } else {
            setFormData({ ...formData, roles: [...current, roleId] });
        }
    };

    const COLUMNS = [
        { 
            key: 'email', label: 'Usuario',
            render: (v, row) => (
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontWeight: 'bold' }}>{row.first_name} {row.last_name}</span>
                    <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>{v}</span>
                </div>
            )
        },
        { 
            key: 'tenant_info', label: 'Tienda / Origen',
            render: (info) => (
                info ? (
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={{ fontSize: '13px', fontWeight: '500' }}>{info.nombre_tienda}</span>
                        <Badge variant="outline" size="sm">{info.schema}</Badge>
                    </div>
                ) : <Badge variant="secondary">Global / Público</Badge>
            )
        },
        { 
            key: 'roles_detalles', label: 'Roles',
            render: (roles) => (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {roles?.map(r => <Badge key={r.id} variant="secondary" size="sm">{r.nombre}</Badge>)}
                    {!roles?.length && <span style={{ fontSize: '12px', color: '#999' }}>Sin roles</span>}
                </div>
            )
        },
        { 
            key: 'is_active', label: 'Estado',
            render: (v) => (
                <Badge variant={v ? 'success' : 'danger'}>
                    {v ? 'Activo' : 'Inactivo'}
                </Badge>
            )
        },
        {
            key: 'id', label: 'Acciones', align: 'right',
            render: (id, row) => {
                const isMe = row.email === currentUserEmail;
                const targetIsAdmin = row.is_staff || row.is_superuser;
                const canEdit = isMe || currentUserIsAdmin || !targetIsAdmin;
                
                return (
                    <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        {isMe ? (
                            <span style={{ fontSize: '12px', color: '#64748b', fontStyle: 'italic', padding: '6px' }}>Es tu cuenta</span>
                        ) : !canEdit ? (
                            <span style={{ fontSize: '12px', color: '#ef4444', fontStyle: 'italic', padding: '6px' }}>No editable</span>
                        ) : (
                            <>
                                <Button variant="ghost" size="sm" onClick={() => {
                                    setEditingId(id);
                                    setFormData({
                                        email: row.email,
                                        first_name: row.first_name || '',
                                        last_name: row.last_name || '',
                                        password: '',
                                        is_active: row.is_active,
                                        is_staff: row.is_staff,
                                        is_superuser: row.is_superuser,
                                        tenant: row.tenant || '',
                                        roles: row.roles || []
                                    });
                                    setIsModalOpen(true);
                                }}>
                                    <Edit size={14} />
                                </Button>
                                <Button variant="ghost" size="sm" onClick={() => handleDelete(id)}>
                                    <Trash2 size={14} color="var(--color-danger)" />
                                </Button>
                            </>
                        )}
                    </div>
                );
            }
        }
    ];

    return (
        <AppView title="Gestionar Usuarios" subtitle="Administra las cuentas de acceso y roles del personal">
            <DataTable
                title="Lista de Usuarios"
                columns={COLUMNS}
                data={users}
                loading={loading}
                actions={
                    <Button onClick={() => { 
                        setEditingId(null); 
                        setFormData({ email: '', first_name: '', last_name: '', password: '', is_active: true, is_staff: false, is_superuser: false, tenant: '', roles: [] }); 
                        setIsModalOpen(true); 
                    }}>
                        <Plus size={18} style={{ marginRight: '8px' }} /> Nuevo Usuario
                    </Button>
                }
            />

            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={editingId ? "Editar Usuario" : "Nuevo Usuario"}
                footer={
                    <>
                        <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancelar</Button>
                        <Button onClick={handleSave}>Guardar Usuario</Button>
                    </>
                }
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <Input 
                            label="Correo Electrónico" 
                            icon={Mail}
                            value={formData.email} 
                            onChange={e => setFormData({...formData, email: e.target.value})} 
                        />
                        <Input 
                            label="Contraseña" 
                            type="password"
                            placeholder={editingId ? "Manten anterior" : "Mínimo 8 caracteres"}
                            value={formData.password} 
                            onChange={e => setFormData({...formData, password: e.target.value})} 
                        />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <Input label="Nombre" value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} />
                        <Input label="Apellidos" value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} />
                    </div>

                    {isPublic && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Tienda Asociada (Opcional)</label>
                            <select 
                                value={formData.tenant} 
                                onChange={e => setFormData({...formData, tenant: e.target.value})}
                                style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', fontSize: '14px' }}
                            >
                                <option value="">--- Acceso Global / Sin Tienda ---</option>
                                {tenants.map(t => (
                                    <option key={t.id} value={t.id}>{t.nombre_comercial} ({t.schema_name})</option>
                                ))}
                            </select>
                        </div>
                    )}

                    <div style={{ padding: '16px', background: 'var(--color-bg-alt, #f8fafc)', borderRadius: '12px', border: '1px solid var(--color-border)' }}>
                        <label style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '12px', display: 'block' }}>Configuración de Acceso</label>
                        
                        <div style={{ display: 'flex', gap: '20px', marginBottom: '16px' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px' }}>
                                <input type="checkbox" checked={formData.is_active} onChange={e => setFormData({...formData, is_active: e.target.checked})} />
                                Cuenta Activa
                            </label>
                            {isPublic && (
                                <>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px' }}>
                                        <input type="checkbox" checked={formData.is_staff} onChange={e => setFormData({...formData, is_staff: e.target.checked})} />
                                        Staff de Tienda (Dueño)
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px' }}>
                                        <input type="checkbox" checked={formData.is_superuser} onChange={e => setFormData({...formData, is_superuser: e.target.checked})} />
                                        Super Usuario (Global)
                                    </label>
                                </>
                            )}
                        </div>

                        <label style={{ fontSize: '11px', color: '#64748b', marginBottom: '8px', display: 'block' }}>ROLES ASIGNADOS:</label>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {roles
                                .filter(r => isPublic || !['super usuario', 'administrador'].includes(r.nombre.toLowerCase()))
                                .map(r => (
                                <div 
                                    key={r.id}
                                    onClick={() => toggleRole(r.id)}
                                    style={{
                                        padding: '6px 12px',
                                        borderRadius: '20px',
                                        border: `1px solid ${formData.roles.includes(r.id) ? 'var(--color-primary)' : 'var(--color-border)'}`,
                                        background: formData.roles.includes(r.id) ? 'var(--color-primary-light, #eef2ff)' : 'white',
                                        color: formData.roles.includes(r.id) ? 'var(--color-primary)' : 'var(--color-text-muted)',
                                        fontSize: '11px',
                                        fontWeight: '600',
                                        cursor: 'pointer'
                                    }}
                                >
                                    {r.nombre}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </Modal>
        </AppView>
    );
}
