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
    ArrowLeft
} from 'lucide-react';
import { productosApi, categoriasApi } from '../../productos_catalogo/services/productosApi';
import { Button, Spinner } from 'shared/components';
import { useCart } from '../hooks/useCart';
import api from 'core/services/api';
import { getBaseDomain, isBaseDomain } from 'core/utils/domain';
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

    // --- Recomendaciones del carrito ---
    const [recommendations, setRecommendations] = useState([]);
    const [loadingRecs, setLoadingRecs] = useState(false);
    const lastProductId = cart.length > 0 ? cart[cart.length - 1].id : null;

    useEffect(() => {
        if (lastProductId && isCartOpen) {
            setLoadingRecs(true);
            api.get(`/productos/${lastProductId}/recomendaciones/`)
                .then(res => setRecommendations(res.data.recommendations || []))
                .catch(() => setRecommendations([]))
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

    const handleCheckout = async () => {
        if (cart.length === 0 || checkoutInProgress.current) return;
        checkoutInProgress.current = true;
        setIsCheckingOut(true);
        let pedidoId = null;

        try {
            // 1. Crear el pedido primero
            const pedidoRes = await api.post('/pedidos/', {
                productos: cart.map(item => ({
                    producto_id: item.id,
                    cantidad: item.quantity,
                    precio_unitario: item.precio
                })),
                total: total
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
            const errorMsg = err.response?.data?.error || err.message || 'Error desconocido';
            console.error("Mensaje del servidor:", errorMsg);
            
            if (pedidoId) {
                console.log("Limpiando pedido huérfano...", pedidoId);
                await api.delete(`/pedidos/${pedidoId}/`).catch(e => console.error("No se pudo limpiar pedido huérfano", e));
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
                                            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
                                                Stock disponible: <strong>{prod.stock}</strong>
                                            </div>
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
                                <h2 className={styles.detailName}>{selectedProduct.nombre}</h2>
                            </div>

                            <div className={styles.detailPrice}>
                                <span className={styles.cur}>Bs.</span>
                                <span className={styles.val}>{parseFloat(selectedProduct.precio).toFixed(2)}</span>
                            </div>

                            <p className={styles.detailDesc}>
                                {selectedProduct.descripcion || 'Sin descripción disponible para este producto.'}
                            </p>

                            <div className={styles.detailMeta}>
                                <div className={styles.metaItem}>
                                    <span className={styles.metaLabel}>Disponibilidad</span>
                                    <span className={`${styles.metaValue} ${selectedProduct.stock > 0 ? styles.stockOk : styles.stockOut}`}>
                                        {selectedProduct.stock > 0 ? `${selectedProduct.stock} unidades` : 'Agotado'}
                                    </span>
                                </div>
                                <div className={styles.metaItem}>
                                    <span className={styles.metaLabel}>Código de producto</span>
                                    <span className={styles.metaValue}>#PRD-{selectedProduct.id}</span>
                                </div>
                            </div>

                            <div className={styles.detailActions}>
                                <Button 
                                    variant="primary"
                                    onClick={() => {
                                        if (selectedProduct.stock > 0) {
                                            addToCart(selectedProduct);
                                            setSelectedProduct(null);
                                        }
                                    }}
                                    disabled={selectedProduct.stock <= 0}
                                >
                                    <ShoppingCart size={20} style={{marginRight: '10px'}} />
                                    {selectedProduct.stock > 0 ? 'Agregar al carrito' : 'Agotado'}
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PublicStorefront;
