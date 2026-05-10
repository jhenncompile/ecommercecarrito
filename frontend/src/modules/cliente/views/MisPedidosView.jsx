import React, { useState, useEffect } from 'react';
import { Package, Calendar, ChevronRight } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import api from 'core/services/api';
import { getBaseDomain } from 'core/utils/domain';
import { Spinner } from 'shared/components';
import styles from './ClientePortal.module.css';

const MisPedidosView = () => {
    const [pedidos, setPedidos] = useState([]);
    const [loading, setLoading] = useState(true);

    const [isGlobal, setIsGlobal] = useState(false);

    useEffect(() => {
        // Manejar retorno de Stripe
        const params = new URLSearchParams(window.location.search);
        if (params.get('status') === 'success') {
            const pedidoId = params.get('pedido_id');
            const tenant = params.get('tenant');
            if (pedidoId) {
                api.post('/pagos/confirm-success/', { pedido_id: pedidoId, tenant: tenant })
                    .then(() => {
                        window.history.replaceState({}, document.title, window.location.pathname);
                        alert("¡Pago confirmado exitosamente!");
                    })
                    .catch(err => console.error("Error confirmando pago:", err));
            }
        }

        const hostname = window.location.hostname;
        const isBase = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '192.168.100.244';
        setIsGlobal(isBase);

        const fetchPedidos = async () => {
            try {
                // Si estamos en el dominio base, buscamos en todas las tiendas
                const endpoint = isBase ? '/pedidos/global-list/' : '/pedidos/';
                const res = await api.get(endpoint);
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
            subtitle={isGlobal ? "Historial de compras en toda la red" : "Historial de compras en esta tienda"}
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
                                <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    <span className={styles.orderTotal}>BS. {parseFloat(pedido.total_pedido || 0).toFixed(2)}</span>
                                    
                                    {pedido.estado.toLowerCase() === 'pendiente' && (
                                        <button 
                                            className={styles.payBtn}
                                            onClick={async (e) => {
                                                e.stopPropagation();
                                                const btn = e.currentTarget;
                                                if (btn.disabled) return;
                                                
                                                btn.disabled = true;
                                                const originalText = btn.innerText;
                                                btn.innerText = "Procesando...";

                                                try {
                                                    const tenantHost = isGlobal ? `${pedido.schema_name}.${getBaseDomain(window.location.hostname)}` : window.location.hostname;
                                                    const apiPort = process.env.REACT_APP_DJANGO_PORT || '8001';
                                                    const baseUrl = `${window.location.protocol}//${tenantHost}:${apiPort}/api`;
                                                    
                                                    const res = await api.post(`${baseUrl}/pagos/create-checkout-session/`, {
                                                        pedido_id: pedido.id,
                                                        success_url: window.location.href + (window.location.href.includes('?') ? '&' : '?') + `status=success&pedido_id=${pedido.id}&tenant=${pedido.schema_name}`,
                                                        cancel_url: window.location.href
                                                    });
                                                    
                                                    if (res.data.url) {
                                                        window.location.href = res.data.url;
                                                    }
                                                } catch (err) {
                                                    btn.disabled = false;
                                                    btn.innerText = originalText;
                                                    alert("No se pudo iniciar el proceso de pago.");
                                                }
                                            }}
                                        >
                                            Pagar ahora
                                        </button>
                                    )}

                                    {pedido.estado.toLowerCase() === 'pagado' && (
                                        <button 
                                            className={styles.downloadBtn}
                                            onClick={async (e) => {
                                                e.stopPropagation();
                                                try {
                                                    const res = await api.get(`/facturas/?pedido=${pedido.id}`);
                                                    const factura = res.data?.results?.[0] || res.data?.[0];
                                                    if (factura) {
                                                        const tenantHost = isGlobal ? `${pedido.schema_name}.${getBaseDomain(window.location.hostname)}` : window.location.hostname;
                                                        const apiPort = process.env.REACT_APP_DJANGO_PORT || '8001';
                                                        const baseUrl = `${window.location.protocol}//${tenantHost}:${apiPort}/api`;
                                                        
                                                        // Descargar con autenticación (blob) usando URL dinámica
                                                        const pdfRes = await api.get(`${baseUrl}/facturas/${factura.nro}/descargar_pdf/`, {
                                                            responseType: 'blob'
                                                        });
                                                        const url = window.URL.createObjectURL(new Blob([pdfRes.data]));
                                                        const link = document.createElement('a');
                                                        link.href = url;
                                                        link.setAttribute('download', `factura-${factura.nro}.pdf`);
                                                        document.body.appendChild(link);
                                                        link.click();
                                                        link.remove();
                                                    }
                                                } catch (err) {
                                                    alert("No se pudo obtener la factura.");
                                                }
                                            }}
                                        >
                                            Descargar Factura
                                        </button>
                                    )}
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
