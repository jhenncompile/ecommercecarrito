import React, { useState, useEffect, useCallback } from 'react';
import { getBaseDomain } from 'core/utils/domain';
import {
    Search,
    ArrowUpDown,
    LayoutGrid,
    List as ListIcon,
    Filter,
    X,
    ImageOff,
    ShoppingCart
} from 'lucide-react';
import { productosApi, categoriasApi } from '../../productos_catalogo/services/productosApi';
import { Button, Badge, Spinner } from 'shared/components';
import { useCart } from '../hooks/useCart';
import api from 'core/services/api';
import styles from './PublicStorefront.module.css';

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
    const [attributes, setAttributes] = useState({}); // { color: 'rojo', talla: 'M' }
    const [sortBy, setSortBy] = useState('-creado_en');
    const [viewMode, setViewMode] = useState('grid');
    const [showMobileFilters, setShowMobileFilters] = useState(false);
    const [isCheckingOut, setIsCheckingOut] = useState(false);

    // --- Carrito ---
    const { cart, addToCart, removeFromCart, updateQuantity, total, clearCart } = useCart();
    const [isCartOpen, setIsCartOpen] = useState(false);

    // --- Recomendaciones ---
    const [recommendations, setRecommendations] = useState([]);
    const [loadingRecs, setLoadingRecs] = useState(false);
    const lastProductId = cart.length > 0 ? cart[cart.length - 1].id : null;

    useEffect(() => {
        if (lastProductId && isCartOpen) {
            setLoadingRecs(true);
            api.get(`/productos/${lastProductId}/recomendaciones/`)
                .then(res => setRecommendations(res.data.recommendations || []))
                .catch(err => setRecommendations([]))
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
                const tenant = query.get('tenant') || window.location.hostname.split('.')[0];
                api.post('/pagos/confirm-success/', {
                    pedido_id: pid,
                    tenant: tenant
                }).catch(e => console.error("Error confirmando éxito", e));
            }
            // Limpiar URL
            window.history.replaceState({}, '', window.location.pathname);
        }
    }, [clearCart]);

    const handleCheckout = async () => {
        if (cart.length === 0) return;
        setIsCheckingOut(true);
        try {
            // 1. Crear el pedido primero
            const pedidoRes = await api.post('/pedidos/', {
                items: cart.map(item => ({
                    producto: item.id,
                    cantidad: item.quantity,
                    precio_unitario: item.precio
                })),
                total: total
            });

            const pedidoId = pedidoRes.data.id;

            // 2. Crear sesión de Stripe dinámica
            const baseDomain = getBaseDomain(window.location.hostname);
            // Si hay un puerto en la URL actual, lo mantenemos (ej. 3000 en dev)
            const currentPort = window.location.port ? `:${window.location.port}` : '';
            const tenantSub = window.location.hostname.split('.')[0];

            const successUrl = `${window.location.protocol}//${baseDomain}${currentPort}/mi-portal?status=success&pedido_id=${pedidoId}&tenant=${tenantSub}`;

            const stripeRes = await api.post('/pagos/create-checkout-session/', {
                pedido_id: pedidoId,
                success_url: successUrl,
                cancel_url: `${window.location.origin}?status=cancel`
            });

            if (stripeRes.data.url) {
                window.location.href = stripeRes.data.url;
            }
        } catch (err) {
            setError('Error al procesar el pago. Inténtalo de nuevo.');
        } finally {
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

                    {/* Atributos (Ejemplo: Talla/Color) */}
                    <div className={styles.filterSection}>
                        <h4>Talla</h4>
                        <div className={styles.tagGroup}>
                            {['S', 'M', 'L', 'XL'].map(talla => (
                                <button
                                    key={talla}
                                    className={attributes.talla === talla ? styles.activeTag : ''}
                                    onClick={() => handleAttrChange('talla', talla)}
                                >
                                    {talla}
                                </button>
                            ))}
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
                                    <div key={prod.id} className={styles.productCard}>
                                        <div className={styles.imageBox}>
                                            {prod.imagen_url ? (
                                                <img src={prod.imagen_url} alt={prod.nombre} />
                                            ) : (
                                                <div className={styles.noImage}><ImageOff size={32} /></div>
                                            )}
                                            {prod.stock < 5 && prod.stock > 0 && (
                                                <span className={styles.lowStockBadge}>Últimas unidades</span>
                                            )}
                                        </div>
                                        <div className={styles.productBody}>
                                            <span className={styles.categoryName}>{prod.categoria_detail?.nombre}</span>
                                            <h3 className={styles.productName}>{prod.nombre}</h3>
                                            <div className={styles.priceRow}>
                                                <span className={styles.currency}>Bs.</span>
                                                <span className={styles.priceValue}>{parseFloat(prod.precio).toFixed(2)}</span>
                                            </div>
                                            <button
                                                className={styles.addToCartBtn}
                                                onClick={() => addToCart(prod)}
                                            >
                                                Agregar al carrito
                                            </button>
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
                                                            <button onClick={() => updateQuantity(item.id, 1)}>+</button>
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
                                    <div className={styles.drawerFooter}>
                                        <div className={styles.totalRow}>
                                            <span>Subtotal</span>
                                            <strong>Bs. {total.toFixed(2)}</strong>
                                        </div>
                                        <Button
                                            variant="primary"
                                            fullWidth
                                            loading={isCheckingOut}
                                            onClick={handleCheckout}
                                        >
                                            Pagar ahora
                                        </Button>
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
        </div>
    );
};

export default PublicStorefront;
