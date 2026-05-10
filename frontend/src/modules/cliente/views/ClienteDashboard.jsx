import React, { useState, useEffect } from 'react';
import { Store, ExternalLink, Search } from 'lucide-react';
import api from 'core/services/api';
import AppView from 'shared/widgets/AppView/AppView';

const ClienteDashboard = () => {
    const [shops, setShops] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchShops = async () => {
            try {
                // Confirmar pago si venimos de Stripe
                const params = new URLSearchParams(window.location.search);
                const statusStr = params.get('status');
                const pedidoId = params.get('pedido_id');
                
                if (statusStr === 'success' && pedidoId) {
                    await api.post('/pagos/confirm-success/', { pedido_id: pedidoId });
                    window.history.replaceState({}, document.title, window.location.pathname);
                }

                const res = await api.get('/tiendas-publicas/');
                setShops(res.data.results || []);
            } catch (err) {
                console.error("Error fetching shops", err);
            } finally {
                setLoading(false);
            }
        };
        fetchShops();
    }, []);

    const filteredShops = shops.filter(s => 
        (s.nombre_comercial || s.schema_name).toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <AppView 
            title="Explorar Tiendas" 
            subtitle="Encuentra los mejores productos en nuestra red de negocios"
        >
            <div style={{ marginBottom: '30px', position: 'relative', maxWidth: '500px' }}>
                <Search size={20} style={{ position: 'absolute', left: '15px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                <input 
                    type="text" 
                    placeholder="Buscar tiendas..." 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{ width: '100%', padding: '12px 20px 12px 45px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '15px', outline: 'none' }}
                />
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '50px', color: '#64748b' }}>Cargando tiendas...</div>
            ) : filteredShops.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '50px', color: '#64748b', backgroundColor: '#f8fafc', borderRadius: '15px' }}>
                    <Store size={48} style={{ marginBottom: '15px', opacity: 0.5 }} />
                    <p>No se encontraron tiendas.</p>
                </div>
            ) : (
                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', 
                    gap: '25px' 
                }}>
                    {filteredShops.map(shop => {
                        const port = window.location.port ? `:${window.location.port}` : '';
                        // Calcular sufijo dinámicamente (misma lógica que el backend)
                        const domainMain = process.env.REACT_APP_DOMAIN_MAIN || window.location.hostname;
                        const suffix = (domainMain === 'localhost' || domainMain === '127.0.0.1')
                            ? '.localhost'
                            : `.${domainMain}.nip.io`;
                        // Pasar tokens por URL al /sso del subdominio (cross-subdomain auth)
                        const ssoParams = new URLSearchParams({
                            token: localStorage.getItem('access_token') || '',
                            refresh: localStorage.getItem('refresh_token') || '',
                            full_name: localStorage.getItem('user_full_name') || '',
                            role: localStorage.getItem('user_role') || 'cliente',
                        });
                        const subdomain = shop.subdominio ? shop.subdominio.split('.')[0] : shop.schema_name;
                        const url = `${window.location.protocol}//${subdomain}${suffix}${port}/sso?${ssoParams.toString()}`;
                        
                        return (
                            <a 
                                key={shop.id} 
                                href={url}
                                style={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    textDecoration: 'none',
                                    color: 'inherit',
                                    backgroundColor: '#fff',
                                    borderRadius: '16px',
                                    border: '1px solid #e2e8f0',
                                    overflow: 'hidden',
                                    transition: 'transform 0.2s, box-shadow 0.2s',
                                    cursor: 'pointer',
                                    boxShadow: '0 4px 6px rgba(0,0,0,0.02)'
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.transform = 'translateY(-5px)';
                                    e.currentTarget.style.boxShadow = '0 10px 20px rgba(0,0,0,0.05)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'translateY(0)';
                                    e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.02)';
                                }}
                            >
                                <div style={{ height: '120px', backgroundColor: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                                    {shop.icono ? (
                                        <img src={shop.icono} alt={shop.nombre_comercial} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                    ) : shop.logo_url ? (
                                        <img src={shop.logo_url} alt={shop.nombre_comercial} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                    ) : (
                                        <Store size={40} color="#cbd5e1" />
                                    )}
                                </div>
                                <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                                    <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: 'bold', color: '#0f172a' }}>
                                        {shop.nombre_comercial || shop.schema_name}
                                    </h3>
                                    {shop.categoria_tienda && (
                                        <span style={{ alignSelf: 'flex-start', padding: '4px 10px', backgroundColor: '#e0e7ff', color: '#4338ca', fontSize: '12px', borderRadius: '12px', fontWeight: 'bold', marginBottom: '10px' }}>
                                            {shop.categoria_tienda}
                                        </span>
                                    )}
                                    <div style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', color: '#3b82f6', fontSize: '14px', fontWeight: 'bold' }}>
                                        Visitar Tienda <ExternalLink size={14} style={{ marginLeft: '6px' }} />
                                    </div>
                                </div>
                            </a>
                        );
                    })}
                </div>
            )}
        </AppView>
    );
};

export default ClienteDashboard;
