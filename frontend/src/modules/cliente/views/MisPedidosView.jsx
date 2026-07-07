import React, { useState, useEffect } from 'react';
import { Package, Calendar, ChevronRight } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import api from 'core/services/api';
import { getBaseDomain, isBaseDomain } from 'core/utils/domain';
import { Spinner } from 'shared/components';
import styles from './ClientePortal.module.css';

const MisPedidosView = () => {
    const [pedidos, setPedidos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedPedidoId, setExpandedPedidoId] = useState(null);

    const [isGlobal, setIsGlobal] = useState(false);

    useEffect(() => {
        // Manejar retorno de Stripe
        const params = new URLSearchParams(window.location.search);
        if (params.get('status') === 'success') {
            const pedidoId = params.get('pedido_id');
            let tenant = params.get('tenant');
            // El param puede llegar como el string "undefined"/"null" cuando el
            // pedido venía del endpoint por-tienda (que no incluye schema_name).
            // En ese caso lo derivamos del subdominio actual (que ES la tienda).
            if (!tenant || tenant === 'undefined' || tenant === 'null') {
                const host = window.location.hostname;
                tenant = isBaseDomain(host) ? 'public' : host.split('.')[0];
            }
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
        const isBase = isBaseDomain(hostname);
        setIsGlobal(isBase);

        const fetchPedidos = async () => {
            try {
                // Si estamos en el dominio base, buscamos en todas las tiendas
                const baseUrl = isBase ? '/pedidos/global-list/' : '/pedidos/';
                const endpoint = `${baseUrl}?_t=${new Date().getTime()}`;
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
        
        // Auto-refresh cada 5 segundos para mantener el estado sincronizado en vivo
        const intervalId = setInterval(fetchPedidos, 5000);
        return () => clearInterval(intervalId);
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
                        {pedidos.map(pedido => {
                            const isExpanded = expandedPedidoId === `${pedido.schema_name}_${pedido.id}`;
                            
                            return (
                            <div key={`${pedido.schema_name || 'tenant'}_${pedido.id}`} 
                                 className={`${styles.orderItem} ${isExpanded ? styles.expanded : ''}`}
                                 style={{ display: 'flex', flexDirection: 'column', gap: '0' }}
                            >
                                {/* Header del Pedido */}
                                <div 
                                    style={{ display: 'flex', alignItems: 'center', width: '100%', cursor: 'pointer', padding: '16px' }}
                                    onClick={() => setExpandedPedidoId(isExpanded ? null : `${pedido.schema_name}_${pedido.id}`)}
                                >
                                    <div className={styles.orderIcon}>
                                        <Package size={20} />
                                    </div>
                                    <div className={styles.orderInfo}>
                                        <span className={styles.orderId}>Pedido #{pedido.schema_name ? `${pedido.schema_name.toUpperCase()}-` : ''}{pedido.id}</span>
                                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                            <Calendar size={12} />
                                            <span className={styles.orderDate}>{new Date(pedido.fecha_creacion).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                    <div className={styles.orderStatus} style={{ flex: 1, padding: '0 20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 'bold' }}>
                                            <span style={{ color: ['PENDIENTE', 'PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-primary)' : '' }}>PENDIENTE</span>
                                            <span style={{ color: ['PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-info)' : '' }}>PAGADO</span>
                                            <span style={{ color: ['PROCESADO', 'ENVIADO', 'ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-warning)' : '' }}>PROCESADO</span>
                                            <span style={{ color: ['ENVIADO', 'ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-success)' : '' }}>ENVIADO</span>
                                            <span style={{ color: ['ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-success)' : '' }}>ENTREGADO</span>
                                        </div>
                                        <div style={{ display: 'flex', height: '6px', background: 'var(--color-surface-2)', borderRadius: '3px', overflow: 'hidden' }}>
                                            <div style={{ flex: 1, background: ['PENDIENTE', 'PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-primary)' : 'transparent' }}></div>
                                            <div style={{ flex: 1, background: ['PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-info)' : 'transparent' }}></div>
                                            <div style={{ flex: 1, background: ['PROCESADO', 'ENVIADO', 'ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-warning)' : 'transparent' }}></div>
                                            <div style={{ flex: 1, background: ['ENVIADO', 'ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-success)' : 'transparent' }}></div>
                                            <div style={{ flex: 1, background: ['ENTREGADO'].includes(pedido.estado.toUpperCase()) ? 'var(--color-success)' : 'transparent' }}></div>
                                        </div>
                                        <span className={`${styles.statusBadge} ${styles[pedido.estado.toLowerCase()] || ''}`} style={{ alignSelf: 'flex-start' }}>
                                            {pedido.estado}
                                        </span>
                                    </div>
                                    <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', gap: '8px', marginLeft: 'auto', marginRight: '16px' }}>
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

                                                        // En modo por-tienda el pedido NO trae schema_name; el tenant
                                                        // correcto es el subdominio actual. Evita mandar "tenant=undefined".
                                                        const tenantSchema = isGlobal ? pedido.schema_name : window.location.hostname.split('.')[0];

                                                        const res = await api.post(`${baseUrl}/pagos/create-checkout-session/`, {
                                                            pedido_id: pedido.id,
                                                            success_url: window.location.href + (window.location.href.includes('?') ? '&' : '?') + `status=success&pedido_id=${pedido.id}&tenant=${tenantSchema}`,
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
                                                        const tenantHost = isGlobal ? `${pedido.schema_name}.${getBaseDomain(window.location.hostname)}` : window.location.hostname;
                                                        const apiPort = process.env.REACT_APP_DJANGO_PORT || '8001';
                                                        const baseUrl = `${window.location.protocol}//${tenantHost}:${apiPort}/api`;
                                                        
                                                        const res = await api.get(`${baseUrl}/facturas/?pedido=${pedido.id}`);
                                                        const factura = res.data?.results?.[0] || res.data?.[0];
                                                        if (factura) {
                                                            
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

                                        {pedido.estado.toLowerCase() === 'enviado' && (
                                            <button 
                                                className={styles.payBtn}
                                                style={{ backgroundColor: 'var(--color-success)', borderColor: 'var(--color-success)' }}
                                                onClick={async (e) => {
                                                    e.stopPropagation();
                                                    if(!window.confirm('¿Confirmas que has recibido tu pedido?')) return;
                                                    
                                                    const btn = e.currentTarget;
                                                    btn.disabled = true;
                                                    try {
                                                        const tenantHost = isGlobal ? `${pedido.schema_name}.${getBaseDomain(window.location.hostname)}` : window.location.hostname;
                                                        const apiPort = process.env.REACT_APP_DJANGO_PORT || '8001';
                                                        const baseUrl = `${window.location.protocol}//${tenantHost}:${apiPort}/api`;
                                                        
                                                        await api.post(`${baseUrl}/pedidos/${pedido.id}/cambiar-estado/`, { estado: 'ENTREGADO' });
                                                        
                                                        // Refrescar lista localmente
                                                        setPedidos(prev => prev.map(p => (p.id === pedido.id && p.schema_name === pedido.schema_name) ? {...p, estado: 'ENTREGADO'} : p));
                                                        alert("¡Pedido finalizado con éxito!");
                                                    } catch (err) {
                                                        btn.disabled = false;
                                                        alert("Error al confirmar entrega.");
                                                    }
                                                }}
                                            >
                                                Marcar como Entregado
                                            </button>
                                        )}
                                    </div>
                                    <ChevronRight 
                                        size={16} 
                                        className={styles.chevron} 
                                        style={{ transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }} 
                                    />
                                </div>

                                {/* Body del Pedido Expandido */}
                                {isExpanded && (
                                    <div style={{ padding: '0 16px 16px 16px', borderTop: '1px solid var(--color-border)', width: '100%', boxSizing: 'border-box' }}>
                                        <h4 style={{ margin: '16px 0 8px 0', fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
                                            Productos del Pedido:
                                        </h4>
                                        <div style={{ backgroundColor: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)', padding: '12px' }}>
                                            {pedido.items && pedido.items.length > 0 ? (
                                                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                                    {pedido.items.map(item => (
                                                        <li key={item.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)' }}>
                                                            <span>{item.cantidad}x {item.producto_nombre}</span>
                                                            <span style={{ fontWeight: '500' }}>Bs. {item.subtotal}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            ) : (
                                                <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)' }}>No se encontraron detalles de productos.</span>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )})}
                    </div>
                )}
            </div>
        </AppView>
    );
};

export default MisPedidosView;
