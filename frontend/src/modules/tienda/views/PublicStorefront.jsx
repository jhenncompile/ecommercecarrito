import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
    Search,
    ArrowUpDown,
    LayoutGrid,
    List as ListIcon,
    Filter,
    X,
    ImageOff,
    ShoppingCart,
    ArrowLeft,
    Bell,
    CheckCircle,
    MessageCircle
} from 'lucide-react';
import { productosApi, categoriasApi } from '../../productos_catalogo/services/productosApi';
import { Button, Spinner } from 'shared/components';
import { useCart } from '../hooks/useCart';
import { enviosApi } from '../services/enviosApi';
import { restockApi } from '../services/restockApi';
import ResenasProducto from '../components/ResenasProducto';
import api from 'core/services/api';
import { getBaseDomain, isBaseDomain } from 'core/utils/domain';
import styles from './PublicStorefront.module.css';

// Departamentos / ciudades de Bolivia para selección de envío
const CIUDADES_BOLIVIA = [
    'La Paz', 'Santa Cruz', 'Cochabamba', 'Oruro', 'Potosí',
    'Chuquisaca', 'Tarija', 'Beni', 'Pando'
];

const normalizarCiudad = (v) => (v || '').trim().toLowerCase();

// Precios calculados por el backend (con fallback al precio crudo)
const getPricing = (p) => {
    const original = parseFloat(p?.precio_original ?? p?.precio) || 0;
    const final = parseFloat(p?.precio_final ?? p?.precio) || 0;
    const preorder = !!p?.en_preventa;
    return { original, final, preorder, hasDiscount: final < original };
};

const PublicStorefront = () => {
    // --- Estado de Datos ---
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // --- Estado de Filtros ---
    const [search, setSearch] = useState('');
    const [selectedCat, setSelectedCat] = useState('');
    const [priceRange, setPriceRange] = useState({ min: '', max: '' });
    const [attributes, setAttributes] = useState({});
    const [sortBy, setSortBy] = useState('-creado_en');
    const [viewMode, setViewMode] = useState('grid');
    const [showMobileFilters, setShowMobileFilters] = useState(false);
    const [isCheckingOut, setIsCheckingOut] = useState(false);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const checkoutInProgress = useRef(false);

    // --- Carrito ---
    const { cart, addToCart, removeFromCart, updateQuantity, total, clearCart } = useCart();
    const [isCartOpen, setIsCartOpen] = useState(false);

    // --- Solicitud de Restock (CU-25) ---
    const [toast, setToast] = useState(null);
    const [restockLoading, setRestockLoading] = useState(false);

    useEffect(() => {
        if (!toast) return;
        const t = setTimeout(() => setToast(null), 3500);
        return () => clearTimeout(t);
    }, [toast]);

    const handleRestockRequest = async (producto) => {
        if (!producto) return;
        const token = localStorage.getItem('access_token');
        if (!token) {
            setToast({ type: 'info', msg: 'Inicia sesión como cliente para recibir el aviso.' });
            return;
        }
        setRestockLoading(true);
        try {
            const res = await restockApi.solicitar(producto.id);
            setToast({ type: 'success', msg: res.data?.mensaje || 'Te avisaremos cuando vuelva a haber stock.' });
        } catch (err) {
            setToast({ type: 'error', msg: err.response?.data?.error || 'No se pudo registrar tu solicitud.' });
        } finally {
            setRestockLoading(false);
        }
    };

    // --- Logística y Envíos (CU-24) ---
    const [shippingConfig, setShippingConfig] = useState({
        ciudad: null, enable_local_delivery: false, enable_national_shipping: true, zonas: []
    });
    const [ciudadCliente, setCiudadCliente] = useState('');
    const [selectedZoneId, setSelectedZoneId] = useState('');

    useEffect(() => {
        enviosApi.obtenerConfig()
            .then(res => setShippingConfig(res.data))
            .catch(() => { /* la tienda no expuso config de envíos */ });
    }, []);

    // Determinar caso de envío según la ciudad seleccionada
    const mismaCiudad = !!ciudadCliente &&
        normalizarCiudad(ciudadCliente) === normalizarCiudad(shippingConfig.ciudad);
    const mostrarZonas = mismaCiudad && shippingConfig.enable_local_delivery;
    const zonaSeleccionada = shippingConfig.zonas.find(z => String(z.id) === String(selectedZoneId));
    const envioCosto = mostrarZonas && zonaSeleccionada ? parseFloat(zonaSeleccionada.price) || 0 : 0;
    const totalConEnvio = total + envioCosto;

    // Datos de envío que se enviarán al crear el pedido
    const buildEnvioPayload = () => {
        if (mostrarZonas && zonaSeleccionada) {
            return {
                tipo_envio: 'LOCAL',
                costo_envio: envioCosto,
                ciudad_envio: ciudadCliente,
                zona_envio: zonaSeleccionada.zone_name,
            };
        }
        if (ciudadCliente && !mismaCiudad && shippingConfig.enable_national_shipping) {
            return {
                tipo_envio: 'ENCOMIENDA',
                costo_envio: 0,
                ciudad_envio: ciudadCliente,
                zona_envio: null,
            };
        }
        return { tipo_envio: null, costo_envio: 0, ciudad_envio: ciudadCliente || null, zona_envio: null };
    };

    // --- Recomendaciones del carrito ---
    const [recommendations, setRecommendations] = useState([]);
    const [loadingRecs, setLoadingRecs] = useState(false);
    const lastProductId = cart.length > 0 ? cart[cart.length - 1].id : null;

    useEffect(() => {
        if (lastProductId && isCartOpen) {
            setLoadingRecs(true);
            // La acción 'recomendaciones' vive en el ViewSet de catálogo
            // (api/catalogo/<id>/recomendaciones/), no en productos.
            api.get(`/catalogo/${lastProductId}/recomendaciones/`)
                .then(res => setRecommendations(res.data.recommendations || []))
                .catch((err) => {
                    console.error('Error cargando recomendaciones del carrito:', err);
                    setRecommendations([]);
                })
                .finally(() => setLoadingRecs(false));
        } else {
            setRecommendations([]);
        }
    }, [lastProductId, isCartOpen]);

    const fetchProducts = useCallback(async () => {
        setLoading(true);
        try {
            const params = {
                search: search || undefined,
                categoria: selectedCat || undefined,
                precio__gte: priceRange.min || undefined,
                precio__lte: priceRange.max || undefined,
                ordering: sortBy,
                activo: true
            };

            // Agregar filtros de atributos dinámicos
            Object.keys(attributes).forEach(key => {
                if (attributes[key]) {
                    params[`attr_${key}`] = attributes[key];
                }
            });

            const res = await productosApi.listar(params);
            setProducts(Array.isArray(res.data) ? res.data : res.data?.results || []);
        } catch (err) {
            setError('Error al conectar con la tienda.');
        } finally {
            setLoading(false);
        }
    }, [search, selectedCat, priceRange, attributes, sortBy]);

    useEffect(() => {
        const delayDebounce = setTimeout(() => {
            fetchProducts();
        }, 300);
        return () => clearTimeout(delayDebounce);
    }, [fetchProducts]);

    useEffect(() => {
        categoriasApi.listar().then(res => {
            setCategories(Array.isArray(res.data) ? res.data : res.data?.results || []);
        });
    }, []);

    const handleAttrChange = (key, value) => {
        setAttributes(prev => ({
            ...prev,
            [key]: prev[key] === value ? '' : value
        }));
    };

    const [paymentSuccess, setPaymentSuccess] = useState(false);
    const [lastPedidoId, setLastPedidoId] = useState(null);

    useEffect(() => {
        const query = new URLSearchParams(window.location.search);
        if (query.get('status') === 'success') {
            setPaymentSuccess(true);
            const pid = query.get('pedido_id');
            setLastPedidoId(pid);
            clearCart();
            // Confirmar en el backend por si el webhook se retrasa
            if (pid) {
                let tenant = query.get('tenant');
                if (!tenant) {
                    const host = window.location.hostname;
                    tenant = isBaseDomain(host) ? 'public' : host.split('.')[0];
                }
                api.post('/pagos/confirm-success/', {
                    pedido_id: pid,
                    tenant: tenant
                }).catch(e => console.error("Error confirmando éxito", e));
            }
            // Limpiar URL
            window.history.replaceState({}, '', window.location.pathname);
        }
    }, [clearCart]);

    // Finalizar el pedido por WhatsApp (no crea pedido; lo gestiona el vendedor)
    const handleWhatsappCheckout = () => {
        if (cart.length === 0) return;

        const numero = (shippingConfig.whatsapp || '').replace(/\D/g, '');
        if (!numero) {
            setToast({ type: 'info', msg: 'Esta tienda aún no configuró un número de WhatsApp.' });
            return;
        }

        const nombreCliente = localStorage.getItem('user_full_name') || 'Cliente';

        const lineas = cart.map(item => {
            const pu = parseFloat(item.precio_final ?? item.precio) || 0;
            return `• ${item.nombre} x${item.quantity} — Bs. ${(pu * item.quantity).toFixed(2)}`;
        });

        let mensaje = `¡Hola! Soy ${nombreCliente} y quiero finalizar mi pedido:\n\n`;
        mensaje += lineas.join('\n');
        if (envioCosto > 0) {
            mensaje += `\n\nEnvío${zonaSeleccionada ? ` (${zonaSeleccionada.zone_name})` : ''}: Bs. ${envioCosto.toFixed(2)}`;
        }
        mensaje += `\n\n*Total: Bs. ${totalConEnvio.toFixed(2)}*`;

        const url = `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`;
        window.open(url, '_blank', 'noopener,noreferrer');
    };

    const handleCheckout = async () => {
        if (cart.length === 0 || checkoutInProgress.current) return;
        checkoutInProgress.current = true;
        setIsCheckingOut(true);
        let pedidoId = null;

        try {
            // 1. Crear el pedido primero (incluye datos de envío CU-24)
            const pedidoRes = await api.post('/pedidos/', {
                productos: cart.map(item => ({
                    producto_id: item.id,
                    cantidad: item.quantity,
                    precio_unitario: item.precio
                })),
                total: totalConEnvio,
                ...buildEnvioPayload()
            });

            pedidoId = pedidoRes.data.id;

            // La URL de retorno es la misma página del catálogo (donde el usuario ya está)
            // Stripe agregará el status al regresar para que mostremos confirmación
            const currentUrl = window.location.href.split('?')[0]; // URL limpia sin params anteriores
            
            const host = window.location.hostname;
            const tenantStr = isBaseDomain(host) ? 'public' : host.split('.')[0];

            const successUrl = `${currentUrl}?status=success&pedido_id=${pedidoId}&tenant=${tenantStr}`;

            const stripeRes = await api.post('/pagos/create-checkout-session/', {
                pedido_id: pedidoId,
                success_url: successUrl,
                cancel_url: `${currentUrl}?status=cancel`
            });

            if (stripeRes.data.url) {
                window.location.href = stripeRes.data.url;
            }
        } catch (err) {
            console.error("❌ ERROR DETALLADO EN CHECKOUT:", err);
            // El límite de plan puede llegar como clave directa {limite_alcanzado: ...}
            // o anidado dentro de la cadena {error: "{'limite_alcanzado': ...}"}.
            const data = err.response?.data || {};
            const errorMsg = data.error || err.message || 'Error desconocido';
            const esLimite = Boolean(data.limite_alcanzado) ||
                (typeof errorMsg === 'string' && errorMsg.includes('limite_alcanzado'));
            console.error("Mensaje del servidor:", errorMsg);

            if (pedidoId) {
                console.log("Limpiando pedido huérfano...", pedidoId);
                await api.delete(`/pedidos/${pedidoId}/`).catch(e => console.error("No se pudo limpiar pedido huérfano", e));
            }

            if (esLimite) {
                // Esta tienda alcanzó el tope de facturación/ventas de su plan.
                setToast({
                    type: 'error',
                    msg: 'No se pudo completar el pago: esta tienda alcanzó el límite de su cuenta. Intenta más tarde.'
                });
            } else {
                setToast({ type: 'error', msg: `No se pudo procesar el pago: ${errorMsg}` });
            }
            setError(`Error al procesar el pago: ${errorMsg}`);
        } finally {
            checkoutInProgress.current = false;
            setIsCheckingOut(false);
        }
    };

    const clearFilters = () => {
        setSearch('');
        setSelectedCat('');
        setPriceRange({ min: '', max: '' });
        setAttributes({});
        setSortBy('-creado_en');
    };

    return (
        <div className={styles.storeContainer}>
            {/* --- MODAL ÉXITO PAGO --- */}
            {paymentSuccess && (
                <div className={styles.successOverlay}>
                    <div className={styles.successCard}>
                        <div className={styles.successIcon}>✅</div>
                        <h2>¡Pago Confirmado!</h2>
                        <p>Gracias por tu compra. Tu pedido #{lastPedidoId} está siendo procesado.</p>
                        <div className={styles.successActions}>
                            <Button
                                variant="primary"
                                onClick={async () => {
                                    try {
                                        // Buscar la factura asociada al pedido
                                        const res = await api.get(`/facturas/?pedido=${lastPedidoId}`);
                                        const factura = res.data.results ? res.data.results[0] : res.data[0];
                                        if (factura) {
                                            // Descargar con autenticación (blob)
                                            const pdfRes = await api.get(`facturas/${factura.nro}/descargar_pdf/`, {
                                                responseType: 'blob'
                                            });
                                            const url = window.URL.createObjectURL(new Blob([pdfRes.data]));
                                            const link = document.createElement('a');
                                            link.href = url;
                                            link.setAttribute('download', `factura-${factura.nro}.pdf`);
                                            document.body.appendChild(link);
                                            link.click();
                                            link.remove();
                                        } else {
                                            alert("La factura aún se está generando, intenta en un momento.");
                                        }
                                    } catch (e) {
                                        console.error("Error al buscar factura", e);
                                    }
                                }}
                            >
                                Descargar Factura PDF
                            </Button>
                            <Button variant="outline" onClick={() => setPaymentSuccess(false)}>Seguir comprando</Button>
                        </div>
                    </div>
                </div>
            )}

            {/* --- HEADER TIENDA --- */}
            <header className={styles.storeHeader}>
                <div className={styles.headerContent}>
                    <div className={styles.backToPortal}>
                        <button 
                            className={styles.backBtn}
                            onClick={() => {
                                const base = getBaseDomain(window.location.hostname);
                                const port = window.location.port ? `:${window.location.port}` : '';
                                window.location.href = `${window.location.protocol}//${base}${port}/mi-portal`;
                            }}
                        >
                            <ArrowLeft size={18} />
                            <span>Regresar al Portal</span>
                        </button>
                    </div>
                    <div className={styles.searchWrapper}>
                        <Search className={styles.searchIcon} size={18} />
                        <input
                            type="text"
                            placeholder="¿Qué estás buscando hoy?..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                    <div className={styles.headerActions}>
                        <div className={styles.totalDisplay}>
                            <span>Total:</span>
                            <strong>Bs. {total.toFixed(2)}</strong>
                        </div>
                        <div className={styles.sellerAccess}>
                            <button 
                                onClick={() => {
                                    const base = getBaseDomain(window.location.hostname);
                                    const port = window.location.port ? `:${window.location.port}` : '';
                                    window.location.href = `${window.location.protocol}//${base}${port}/login`;
                                }}
                                className={styles.sellerLink}
                            >
                                Acceso Vendedor
                            </button>
                        </div>
                        <button
                            className={styles.cartBtn}
                            title="Ver Carrito"
                            onClick={() => setIsCartOpen(true)}
                        >
                            <ShoppingCart size={20} />
                            <span className={styles.cartBadge}>{cart.length}</span>
                        </button>
                        {cart.length > 0 && (
                            <Button
                                variant="primary"
                                size="sm"
                                loading={isCheckingOut}
                                onClick={handleCheckout}
                            >
                                Pagar ahora
                            </Button>
                        )}
                    </div>
                </div>
            </header>

            <main className={styles.mainLayout}>
                {/* --- SIDEBAR FILTROS (Desktop) --- */}
                <aside className={`${styles.filterSidebar} ${showMobileFilters ? styles.showMobile : ''}`}>
                    <div className={styles.sidebarHeader}>
                        <h3>Filtros</h3>
                        <button onClick={clearFilters} className={styles.clearBtn}>Limpiar todo</button>
                    </div>

                    {/* Categorías */}
                    <div className={styles.filterSection}>
                        <h4>Categorías</h4>
                        <div className={styles.catLinks}>
                            <button
                                className={!selectedCat ? styles.activeCat : ''}
                                onClick={() => setSelectedCat('')}
                            >
                                Todas
                            </button>
                            {categories.map(cat => (
                                <button
                                    key={cat.id}
                                    className={selectedCat === cat.id ? styles.activeCat : ''}
                                    onClick={() => setSelectedCat(cat.id)}
                                >
                                    {cat.nombre}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Rango de Precio */}
                    <div className={styles.filterSection}>
                        <h4>Rango de Precio (Bs.)</h4>
                        <div className={styles.priceInputs}>
                            <input
                                type="number"
                                placeholder="Min"
                                value={priceRange.min}
                                onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
                            />
                            <span>-</span>
                            <input
                                type="number"
                                placeholder="Max"
                                value={priceRange.max}
                                onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
                            />
                        </div>
                    </div>
                </aside>

                {/* --- CONTENIDO PRINCIPAL --- */}
                <section className={styles.contentArea}>
                    <div className={styles.topToolbar}>
                        <div className={styles.resultsInfo}>
                            <span>Mostrando <strong>{products.length}</strong> productos</span>
                        </div>
                        <div className={styles.toolbarControls}>
                            <div className={styles.sortWrapper}>
                                <ArrowUpDown size={14} />
                                <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                                    <option value="-creado_en">Más recientes</option>
                                    <option value="precio">Precio: Menor a Mayor</option>
                                    <option value="-precio">Precio: Mayor a Menor</option>
                                    <option value="nombre">Nombre A-Z</option>
                                </select>
                            </div>
                            <div className={styles.viewToggle}>
                                <button
                                    className={viewMode === 'grid' ? styles.activeView : ''}
                                    onClick={() => setViewMode('grid')}
                                >
                                    <LayoutGrid size={18} />
                                </button>
                                <button
                                    className={viewMode === 'list' ? styles.activeView : ''}
                                    onClick={() => setViewMode('list')}
                                >
                                    <ListIcon size={18} />
                                </button>
                            </div>
                            <button
                                className={styles.mobileFilterToggle}
                                onClick={() => setShowMobileFilters(!showMobileFilters)}
                            >
                                <Filter size={18} />
                            </button>
                        </div>
                    </div>

                    {loading ? (
                        <div className={styles.loaderWrap}>
                            <Spinner size="lg" />
                            <p>Buscando lo mejor para ti...</p>
                        </div>
                    ) : (
                        <div className={viewMode === 'grid' ? styles.productGrid : styles.productList}>
                            {products.length === 0 ? (
                                <div className={styles.emptyState}>
                                    <ShoppingCart size={64} />
                                    <h3>No encontramos lo que buscas</h3>
                                    <p>Intenta ajustando los filtros o buscando otro término.</p>
                                    <Button onClick={clearFilters}>Ver todo el catálogo</Button>
                                </div>
                            ) : (
                                products.map(prod => (
                                    <div key={prod.id} className={styles.productCard} onClick={() => setSelectedProduct(prod)}>
                                        <div className={styles.imageBox}>
                                            {prod.imagen_url ? (
                                                <img src={prod.imagen_url} alt={prod.nombre} />
                                            ) : (
                                                <div className={styles.noImage}><ImageOff size={32} /></div>
                                            )}
                                            {getPricing(prod).preorder ? (
                                                <span className={styles.lowStockBadge} style={{ background: '#7c3aed' }}>PRE-VENTA</span>
                                            ) : prod.stock <= 0 ? (
                                                <span className={styles.lowStockBadge} style={{ background: '#dc2626' }}>AGOTADO</span>
                                            ) : prod.stock < 5 && prod.stock > 0 && (
                                                <span className={styles.lowStockBadge}>Últimas unidades</span>
                                            )}
                                        </div>
                                        <div className={styles.productBody}>
                                            <span className={styles.categoryName}>{prod.categoria_detail?.nombre}</span>
                                            <h3 className={styles.productName}>{prod.nombre}</h3>
                                            {(() => {
                                                const pr = getPricing(prod);
                                                return (
                                                    <div className={styles.priceRow} style={{ display: 'flex', alignItems: 'baseline', gap: '6px', flexWrap: 'wrap' }}>
                                                        {pr.hasDiscount && (
                                                            <span style={{ fontSize: '13px', color: 'var(--color-text-muted)', textDecoration: 'line-through' }}>
                                                                Bs. {pr.original.toFixed(2)}
                                                            </span>
                                                        )}
                                                        <span className={styles.currency}>Bs.</span>
                                                        <span className={styles.priceValue}>{pr.final.toFixed(2)}</span>
                                                    </div>
                                                );
                                            })()}
                                            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
                                                {getPricing(prod).preorder && prod.estimated_arrival_date
                                                    ? <>Llega aprox: <strong>{prod.estimated_arrival_date}</strong></>
                                                    : <>Stock disponible: <strong>{prod.stock}</strong></>}
                                            </div>
                                            {getPricing(prod).preorder ? (
                                                <button
                                                    className={styles.addToCartBtn}
                                                    style={{ background: '#7c3aed' }}
                                                    onClick={(e) => { e.stopPropagation(); addToCart(prod); }}
                                                >
                                                    Reservar con Descuento
                                                </button>
                                            ) : (
                                                <button
                                                    className={styles.addToCartBtn}
                                                    style={prod.stock <= 0 ? { backgroundColor: 'var(--color-text-muted)', cursor: 'not-allowed' } : {}}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        if (prod.stock > 0) addToCart(prod);
                                                    }}
                                                    disabled={prod.stock <= 0}
                                                >
                                                    {prod.stock <= 0 ? 'Agotado' : 'Agregar al carrito'}
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </section>
            </main>
            {/* --- CART DRAWER --- */}
            {isCartOpen && (
                <div className={styles.cartOverlay} onClick={() => setIsCartOpen(false)}>
                    <div className={`${styles.cartDrawer} ${recommendations.length > 0 ? styles.cartDrawerWide : ''}`} onClick={e => e.stopPropagation()}>
                        <div className={styles.drawerHeader}>
                            <h3>Tu Carrito</h3>
                            <button onClick={() => setIsCartOpen(false)}><X size={24} /></button>
                        </div>

                        {cart.length === 0 ? (
                            <div className={styles.drawerContent}>
                                <div className={styles.emptyCart}>
                                    <ShoppingCart size={48} />
                                    <p>Tu carrito está vacío</p>
                                    <Button onClick={() => setIsCartOpen(false)}>Empezar a comprar</Button>
                                </div>
                            </div>
                        ) : (
                            <div className={styles.cartLayout}>
                                <div className={styles.cartMain}>
                                    <div className={styles.drawerContent}>
                                        <div className={styles.cartItemsList}>
                                            {cart.map(item => (
                                                <div key={item.id} className={styles.cartItemRow}>
                                                    <div className={styles.itemImg}>
                                                        <img src={item.imagen_url || '/placeholder.png'} alt={item.nombre} />
                                                    </div>
                                                    <div className={styles.itemInfo}>
                                                        <h4>{item.nombre}</h4>
                                                        <div className={styles.qtyControls}>
                                                            <button onClick={() => updateQuantity(item.id, -1)}>-</button>
                                                            <span>{item.quantity}</span>
                                                            <button 
                                                                onClick={() => updateQuantity(item.id, 1)}
                                                                disabled={item.quantity >= item.stock}
                                                                style={{ opacity: item.quantity >= item.stock ? 0.5 : 1, cursor: item.quantity >= item.stock ? 'not-allowed' : 'pointer' }}
                                                            >+</button>
                                                        </div>
                                                    </div>
                                                    <div className={styles.itemPrice}>
                                                        <span>Bs. {(item.precio * item.quantity).toFixed(2)}</span>
                                                        <button onClick={() => removeFromCart(item.id)} className={styles.removeBtn}>Eliminar</button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    {/* --- ENVÍO (CU-24) --- */}
                                    <div style={{ padding: '16px', borderTop: '1px solid #e2e8f0' }}>
                                        <label style={{ display: 'block', fontWeight: 600, marginBottom: '8px', color: '#0f172a', fontSize: '14px' }}>
                                            Ciudad / Departamento de entrega
                                        </label>
                                        <select
                                            value={ciudadCliente}
                                            onChange={(e) => { setCiudadCliente(e.target.value); setSelectedZoneId(''); }}
                                            style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1', marginBottom: '10px' }}
                                        >
                                            <option value="">Selecciona tu ciudad...</option>
                                            {CIUDADES_BOLIVIA.map(c => (
                                                <option key={c} value={c}>{c}</option>
                                            ))}
                                        </select>

                                        {/* Caso 1: misma ciudad → selector de zonas */}
                                        {mostrarZonas && (
                                            <div style={{ marginBottom: '4px' }}>
                                                <label style={{ display: 'block', fontWeight: 600, marginBottom: '8px', color: '#0f172a', fontSize: '14px' }}>
                                                    Zona de Delivery
                                                </label>
                                                <select
                                                    value={selectedZoneId}
                                                    onChange={(e) => setSelectedZoneId(e.target.value)}
                                                    style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                                                >
                                                    <option value="">Selecciona una zona...</option>
                                                    {shippingConfig.zonas.map(z => (
                                                        <option key={z.id} value={z.id}>
                                                            {z.zone_name} — Bs. {parseFloat(z.price).toFixed(2)}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>
                                        )}

                                        {/* Caso 2: ciudad distinta → encomienda */}
                                        {ciudadCliente && !mismaCiudad && shippingConfig.enable_national_shipping && (
                                            <div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1', background: '#f8fafc', fontSize: '14px', color: '#0f172a', fontWeight: 600 }}>
                                                    📦 Envío por Encomienda (Pago en Destino)
                                                </div>
                                                <p style={{ marginTop: '8px', padding: '10px', borderRadius: '8px', background: '#fffbeb', border: '1px solid #fde68a', color: '#92400e', fontSize: '13px', lineHeight: 1.4 }}>
                                                    El costo del envío por encomienda varía según la agencia y el peso.
                                                    Usted pagará el envío al recoger su paquete.
                                                </p>
                                            </div>
                                        )}
                                    </div>

                                    <div className={styles.drawerFooter}>
                                        <div className={styles.totalRow}>
                                            <span>Subtotal</span>
                                            <strong>Bs. {total.toFixed(2)}</strong>
                                        </div>
                                        {envioCosto > 0 && (
                                            <div className={styles.totalRow}>
                                                <span>Envío{zonaSeleccionada ? ` (${zonaSeleccionada.zone_name})` : ''}</span>
                                                <strong>Bs. {envioCosto.toFixed(2)}</strong>
                                            </div>
                                        )}
                                        <div className={styles.totalRow}>
                                            <span>Total</span>
                                            <strong>Bs. {totalConEnvio.toFixed(2)}</strong>
                                        </div>
                                        <Button
                                            variant="primary"
                                            fullWidth
                                            loading={isCheckingOut}
                                            onClick={handleCheckout}
                                        >
                                            Pagar ahora
                                        </Button>
                                        {shippingConfig.whatsapp && (
                                            <button
                                                type="button"
                                                onClick={handleWhatsappCheckout}
                                                style={{
                                                    marginTop: '10px', width: '100%', display: 'flex', alignItems: 'center',
                                                    justifyContent: 'center', gap: '8px', padding: '12px', borderRadius: '10px',
                                                    border: 'none', background: '#25D366', color: '#fff', fontWeight: 600,
                                                    fontSize: '15px', cursor: 'pointer',
                                                }}
                                            >
                                                <MessageCircle size={18} />
                                                Finalizar por WhatsApp
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {recommendations.length > 0 && (
                                    <div className={styles.cartSidebar}>
                                        <h4 className={styles.recommendationsTitle}>Sugerencias para completar tu compra</h4>
                                        {loadingRecs ? (
                                            <div className="flex justify-center p-6"><Spinner size="sm" /></div>
                                        ) : (
                                            <div className="grid grid-cols-2 gap-3 mt-4">
                                                {recommendations.map(rec => (
                                                    <div key={rec.id} className={styles.recCard}>
                                                        <div className={styles.recImg}>
                                                            {rec.imagen_url ? (
                                                                <img src={rec.imagen_url} alt={rec.nombre} />
                                                            ) : (
                                                                <ImageOff size={24} color="#cbd5e1" />
                                                            )}
                                                            {rec.score > 0 && (
                                                                <span className={styles.matchBadge}>{Math.round(rec.score * 100)}% Match</span>
                                                            )}
                                                        </div>
                                                        <div className={styles.recInfo}>
                                                            <h5 className={styles.recName}>{rec.nombre}</h5>
                                                            <span className={styles.recPrice}>Bs. {parseFloat(rec.precio).toFixed(2)}</span>
                                                            <button
                                                                className={styles.recAddBtn}
                                                                onClick={() => addToCart(rec)}
                                                            >
                                                                Añadir
                                                            </button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}
            {/* --- PRODUCT DETAIL MODAL --- */}
            {selectedProduct && (
                <div className={styles.detailOverlay} onClick={() => setSelectedProduct(null)}>
                    <div className={styles.detailCard} onClick={e => e.stopPropagation()}>
                        <button className={styles.closeDetail} onClick={() => setSelectedProduct(null)}>
                            <X size={20} />
                        </button>
                        
                        <div className={styles.detailImage}>
                            {selectedProduct.imagen_url ? (
                                <img src={selectedProduct.imagen_url} alt={selectedProduct.nombre} />
                            ) : (
                                <div className={styles.noImage}><ImageOff size={64} /></div>
                            )}
                        </div>

                        <div className={styles.detailContent}>
                            <div className={styles.detailHeader}>
                                <span className={styles.detailCategory}>{selectedProduct.categoria_detail?.nombre}</span>
                                {getPricing(selectedProduct).preorder && (
                                    <span style={{ display: 'inline-block', marginLeft: '8px', padding: '3px 10px', borderRadius: '999px', background: '#7c3aed', color: '#fff', fontSize: '11px', fontWeight: 700, letterSpacing: '0.5px', verticalAlign: 'middle' }}>
                                        PRE-VENTA
                                    </span>
                                )}
                                <h2 className={styles.detailName}>{selectedProduct.nombre}</h2>
                            </div>

                            <div className={styles.detailPrice} style={{ display: 'flex', alignItems: 'baseline', gap: '10px', flexWrap: 'wrap' }}>
                                {getPricing(selectedProduct).hasDiscount && (
                                    <span style={{ fontSize: '18px', color: 'var(--color-text-muted)', textDecoration: 'line-through' }}>
                                        Bs. {getPricing(selectedProduct).original.toFixed(2)}
                                    </span>
                                )}
                                <span>
                                    <span className={styles.cur}>Bs.</span>
                                    <span className={styles.val}>{getPricing(selectedProduct).final.toFixed(2)}</span>
                                </span>
                            </div>

                            <p className={styles.detailDesc}>
                                {selectedProduct.descripcion || 'Sin descripción disponible para este producto.'}
                            </p>

                            <div className={styles.detailMeta}>
                                <div className={styles.metaItem}>
                                    <span className={styles.metaLabel}>Disponibilidad</span>
                                    <span className={`${styles.metaValue} ${selectedProduct.stock > 0 ? styles.stockOk : styles.stockOut}`}>
                                        {selectedProduct.stock > 0 ? `${selectedProduct.stock} unidades` : (getPricing(selectedProduct).preorder ? 'En preventa' : 'Agotado')}
                                    </span>
                                </div>
                                {getPricing(selectedProduct).preorder && selectedProduct.estimated_arrival_date && (
                                    <div className={styles.metaItem}>
                                        <span className={styles.metaLabel}>Llegada estimada</span>
                                        <span className={styles.metaValue}>{selectedProduct.estimated_arrival_date}</span>
                                    </div>
                                )}
                                <div className={styles.metaItem}>
                                    <span className={styles.metaLabel}>Código de producto</span>
                                    <span className={styles.metaValue}>#PRD-{selectedProduct.id}</span>
                                </div>
                            </div>

                            <div className={styles.detailActions}>
                                {getPricing(selectedProduct).preorder ? (
                                    <Button
                                        variant="primary"
                                        style={{ background: '#7c3aed' }}
                                        onClick={() => {
                                            addToCart(selectedProduct);
                                            setSelectedProduct(null);
                                        }}
                                    >
                                        <ShoppingCart size={20} style={{marginRight: '10px'}} />
                                        Reservar con Descuento
                                    </Button>
                                ) : selectedProduct.stock > 0 ? (
                                    <Button
                                        variant="primary"
                                        onClick={() => {
                                            addToCart(selectedProduct);
                                            setSelectedProduct(null);
                                        }}
                                    >
                                        <ShoppingCart size={20} style={{marginRight: '10px'}} />
                                        Agregar al carrito
                                    </Button>
                                ) : (
                                    <Button
                                        variant="primary"
                                        loading={restockLoading}
                                        onClick={() => handleRestockRequest(selectedProduct)}
                                    >
                                        <Bell size={20} style={{marginRight: '10px'}} />
                                        Avisarme cuando vuelva a haber stock
                                    </Button>
                                )}
                            </div>

                            {/* --- Reseñas y Calificaciones (CU-27) --- */}
                            <ResenasProducto
                                productId={selectedProduct.id}
                                onToast={(msg, type) => setToast({ type: type || 'info', msg })}
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* --- TOAST (CU-25) --- */}
            {toast && (
                <div
                    role="status"
                    style={{
                        position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
                        zIndex: 2000, display: 'flex', alignItems: 'center', gap: '10px',
                        padding: '14px 20px', borderRadius: '12px', color: '#fff', fontWeight: 600,
                        fontSize: '14px', boxShadow: '0 10px 30px rgba(0,0,0,0.25)', maxWidth: '90%',
                        background: toast.type === 'success' ? '#16a34a'
                            : toast.type === 'error' ? '#dc2626' : '#334155',
                    }}
                >
                    {toast.type === 'success' ? <CheckCircle size={18} /> : <Bell size={18} />}
                    <span>{toast.msg}</span>
                </div>
            )}
        </div>
    );
};

export default PublicStorefront;
