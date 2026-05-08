import React, { useState, useEffect } from 'react';
import { Package, Search, Calendar, ChevronRight } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import api from 'core/services/api';
import { Spinner, Badge, Button } from 'shared/components';
import styles from './ClientePortal.module.css';

const MisPedidosView = () => {
    const [pedidos, setPedidos] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPedidos = async () => {
            try {
                const res = await api.get('/pedidos/');
                // Manejar tanto lista simple como respuesta paginada
                const data = res.data?.results || res.data || [];
                setPedidos(Array.isArray(data) ? data : []);
            } catch (err) {
                console.error("Error al cargar pedidos:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchPedidos();
    }, []);

    return (
        <AppView 
            title="Mis Pedidos" 
            subtitle="Historial de compras en esta tienda"
        >
            <div className={styles.sectionCard}>
                {loading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
                        <Spinner size="lg" />
                    </div>
                ) : pedidos.length === 0 ? (
                    <div className={styles.empty}>
                        <Package size={48} />
                        <p>Aún no has realizado pedidos en esta tienda.</p>
                    </div>
                ) : (
                    <div className={styles.orderList}>
                        {pedidos.map(pedido => (
                            <div key={pedido.id} className={styles.orderItem}>
                                <div className={styles.orderIcon}>
                                    <Package size={20} />
                                </div>
                                <div className={styles.orderInfo}>
                                    <span className={styles.orderId}>Pedido #{pedido.id}</span>
                                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                        <Calendar size={12} />
                                        <span className={styles.orderDate}>{new Date(pedido.fecha_creacion).toLocaleDateString()}</span>
                                    </div>
                                </div>
                                <div className={styles.orderStatus}>
                                    <span className={`${styles.statusBadge} ${styles[pedido.estado.toLowerCase()] || ''}`}>
                                        {pedido.estado}
                                    </span>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <span className={styles.orderTotal}>BS. {parseFloat(pedido.carrito?.total_carrito || 0).toFixed(2)}</span>
                                </div>
                                <ChevronRight size={16} className={styles.chevron} />
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </AppView>
    );
};

export default MisPedidosView;
