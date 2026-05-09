import React, { useState, useEffect } from 'react';
import { 
    ShoppingBag, 
    Store, 
    CreditCard, 
    ChevronRight, 
    ExternalLink,
    Box,
    Clock
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from 'core/services/api';
import AppView from 'shared/widgets/AppView/AppView';
import StatCard from 'shared/widgets/StatCard/StatCard';
import { getBaseDomain } from 'core/utils/domain';
import styles from './ClientePortal.module.css';

const ClienteDashboard = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState({ orders: 0, spent: 0, pending: 0 });
    const [recentOrders, setRecentOrders] = useState([]);
    const [shops, setShops] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Confirmar pago si venimos de Stripe
                const params = new URLSearchParams(window.location.search);
                const statusStr = params.get('status');
                const pedidoId = params.get('pedido_id');
                
                if (statusStr === 'success' && pedidoId) {
                    await api.post('/pagos/confirm-success/', { pedido_id: pedidoId });
                    // Limpiar la URL para evitar re-confirmaciones
                    window.history.replaceState({}, document.title, window.location.pathname);
                }

                const hostname = window.location.hostname;
                const baseDomain = getBaseDomain(hostname);
                
                // Es público si el hostname es igual al baseDomain
                const isPublic = hostname === baseDomain;
                
                // Solo pedimos pedidos si estamos en un contexto de tenant
                const requests = [api.get('/tiendas-publicas/')];
                if (!isPublic) {
                    requests.push(api.get('/pedidos/'));
                }

                const results = await Promise.allSettled(requests);
                
                const shopsRes = results[0].status === 'fulfilled' ? results[0].value : null;
                const ordersRes = results.length > 1 && results[1].status === 'fulfilled' ? results[1].value : null;

                if (shopsRes) {
                    setShops(shopsRes.data.results || []);
                }

                if (ordersRes) {
                    const orders = ordersRes.data || [];
                    const recentOrders = Array.isArray(orders) ? orders.slice(0, 5) : [];
                    setRecentOrders(recentOrders);
                    setStats({
                        orders: orders.length,
                        spent: orders.reduce((acc, o) => acc + parseFloat(o.total || 0), 0),
                        pending: orders.filter(o => o.estado === 'pendiente').length
                    });
                }
            } catch (err) {
                console.error("Error fetching client data", err);
            }
        };
        fetchData();
    }, []);

    return (
        <AppView 
            title="Portal del Cliente" 
            subtitle="Gestiona tus pedidos y explora tiendas de la red"
        >
            <StatCard.Group>
                <StatCard 
                    label="Mis Pedidos" 
                    value={stats.orders} 
                    icon={<ShoppingBag size={18} />}
                    accentColor="var(--color-primary)"
                />
                <StatCard 
                    label="Pedidos Pendientes" 
                    value={stats.pending} 
                    icon={<Clock size={18} />}
                    accentColor="var(--color-warning)"
                />
                <StatCard 
                    label="Inversión Total" 
                    value={`BS. ${stats.spent.toFixed(2)}`} 
                    icon={<CreditCard size={18} />}
                    accentColor="var(--color-success)"
                />
            </StatCard.Group>

            <div className={styles.dashboardGrid}>
                {/* RECENT ORDERS */}
                <div className={styles.sectionCard}>
                    <div className={styles.sectionHeader}>
                        <h3>Mis pedidos recientes</h3>
                        <button onClick={() => navigate('/pedidos')} className={styles.viewAll}>Ver todo</button>
                    </div>
                    <div className={styles.orderList}>
                        {recentOrders.length === 0 ? (
                            <p className={styles.empty}>Aún no has realizado pedidos.</p>
                        ) : (
                            recentOrders.map(order => (
                                <div key={order.id} className={styles.orderItem}>
                                    <div className={styles.orderIcon}>
                                        <Box size={18} />
                                    </div>
                                    <div className={styles.orderInfo}>
                                        <span className={styles.orderId}>Pedido #{order.id}</span>
                                        <span className={styles.orderDate}>{new Date(order.creado_en).toLocaleDateString()}</span>
                                    </div>
                                    <div className={styles.orderStatus}>
                                        <span className={`${styles.statusBadge} ${styles[order.estado]}`}>
                                            {order.estado}
                                        </span>
                                    </div>
                                    <span className={styles.orderTotal}>BS. {parseFloat(order.total).toFixed(2)}</span>
                                    <ChevronRight size={16} className={styles.chevron} />
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* EXPLORE SHOPS */}
                <div className={styles.sectionCard}>
                    <div className={styles.sectionHeader}>
                        <h3>Explorar Tiendas</h3>
                    </div>
                    <div className={styles.shopGrid}>
                        {shops.map(shop => (
                            <div key={shop.id} className={styles.shopCard}>
                                <div className={styles.shopIcon}>
                                    {shop.logo_url ? (
                                        <img src={shop.logo_url} alt={shop.nombre_comercial} className={styles.shopLogo} />
                                    ) : (
                                        <Store size={24} />
                                    )}
                                </div>
                                <div className={styles.shopDetails}>
                                    <h4>{shop.nombre_comercial}</h4>
                                    <p>{shop.subdominio || `${shop.schema_name}.localhost`}</p>
                                </div>
                                <a 
                                    href={`http://${shop.subdominio || `${shop.schema_name}${process.env.REACT_APP_TENANT_DOMAIN_SUFFIX || '.localhost'}`}${window.location.port ? `:${window.location.port}` : ''}/sso?token=${localStorage.getItem('access_token')}&refresh=${localStorage.getItem('refresh_token')}&full_name=${encodeURIComponent(localStorage.getItem('user_full_name') || '')}&role=${localStorage.getItem('user_role')}`} 
                                    className={styles.shopLink}
                                >
                                    <ExternalLink size={16} />
                                </a>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </AppView>
    );
};

export default ClienteDashboard;
