import React, { useState, useEffect, useCallback } from 'react';
import { 
    Package, 
    AlertCircle, 
    ArrowUpCircle, 
    ArrowDownCircle, 
    Search, 
    RefreshCw, 
    Plus, 
    Minus,
    ClipboardList,
    TrendingDown,
    TrendingUp,
    Edit3,
    Check,
    X
} from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Button, Input, Badge, Alert, Spinner } from 'shared/components';
import StatCard from 'shared/widgets/StatCard/StatCard';
import { productosApi, categoriasApi } from '../../productos_catalogo/services/productosApi';
import styles from './Inventario.module.css';

const InventarioView = () => {
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [search, setSearch] = useState('');
    const [updatingId, setUpdatingId] = useState(null);
    const [adjustmentModal, setAdjustmentModal] = useState({ open: false, product: null, value: 0 });

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [pRes, cRes] = await Promise.all([
                productosApi.listar(),
                categoriasApi.listar()
            ]);
            const getList = (res) => Array.isArray(res.data) ? res.data : res.data?.results || [];
            setProducts(getList(pRes));
            setCategories(getList(cRes));
        } catch (err) {
            setError('Error al cargar datos del inventario.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleStockAdjustment = async (id, currentStock, delta, isAbsolute = false) => {
        const newStock = isAbsolute ? Math.max(0, delta) : Math.max(0, currentStock + delta);
        if (newStock === currentStock && !isAbsolute) return;

        setUpdatingId(id);
        try {
            await productosApi.ajustarStock(id, newStock);
            setProducts(prev => prev.map(p => p.id === id ? { ...p, stock: newStock } : p));
            setAdjustmentModal({ open: false, product: null, value: 0 });
        } catch (err) {
            setError('No se pudo actualizar el stock.');
        } finally {
            setUpdatingId(null);
        }
    };

    const stats = {
        totalItems: products.length,
        totalStock: products.reduce((acc, p) => acc + (p.stock || 0), 0),
        lowStock: products.filter(p => p.stock > 0 && p.stock < 10).length,
        outOfStock: products.filter(p => (p.stock || 0) <= 0).length,
        inventoryValue: products.reduce((acc, p) => acc + (p.stock * p.precio || 0), 0)
    };

    const filteredProducts = products.filter(p => 
        p.nombre.toLowerCase().includes(search.toLowerCase()) || 
        p.sku?.toLowerCase().includes(search.toLowerCase())
    );

    const columns = [
        {
            key: 'nombre',
            label: 'Producto',
            render: (val, row) => (
                <div className={styles.productCell}>
                    <div className={styles.productInfo}>
                        <span className={styles.productName}>{val}</span>
                        <span className={styles.productSku}>{row.sku || 'S/N'}</span>
                    </div>
                </div>
            )
        },
        {
            key: 'categoria_detail',
            label: 'Categoría',
            render: (val) => val?.nombre || 'General'
        },
        {
            key: 'stock',
            label: 'Stock Actual',
            align: 'center',
            render: (val) => (
                <Badge 
                    variant={val <= 0 ? 'danger' : val < 10 ? 'warning' : 'success'} 
                    dot
                >
                    {val} unidades
                </Badge>
            )
        },
        {
            key: 'ajuste',
            label: 'Ajuste Rápido',
            align: 'center',
            render: (val, row) => (
                <div className={styles.adjustmentGroup}>
                    <button 
                        className={styles.adjustBtn} 
                        onClick={() => handleStockAdjustment(row.id, row.stock, -1)}
                        disabled={updatingId === row.id || row.stock <= 0}
                        title="Restar 1"
                    >
                        <Minus size={14} />
                    </button>
                    <span className={styles.stockDisplay}>
                        {updatingId === row.id ? <Spinner size="sm" /> : row.stock}
                    </span>
                    <button 
                        className={styles.adjustBtn} 
                        onClick={() => handleStockAdjustment(row.id, row.stock, 1)}
                        disabled={updatingId === row.id}
                        title="Sumar 1"
                    >
                        <Plus size={14} />
                    </button>
                    <button 
                        className={`${styles.adjustBtn} ${styles.editBtn}`} 
                        onClick={() => setAdjustmentModal({ open: true, product: row, value: row.stock })}
                        disabled={updatingId === row.id}
                        title="Ajuste Manual"
                    >
                        <Edit3 size={14} />
                    </button>
                </div>
            )
        },
        {
            key: 'precio',
            label: 'Valor Unit.',
            render: (val) => `BS. ${parseFloat(val).toFixed(2)}`
        },
        {
            key: 'total_value',
            label: 'Valor Total',
            render: (val, row) => (
                <span className={styles.totalValue}>
                    BS. {(row.stock * row.precio).toFixed(2)}
                </span>
            )
        }
    ];

    return (
        <AppView 
            title="Gestión de Inventario" 
            subtitle="Control de stock y valoración de productos en tiempo real"
            actions={
                <Button 
                    variant="primary" 
                    leftIcon={<RefreshCw size={16} />} 
                    onClick={fetchData}
                    loading={loading}
                >
                    Sincronizar
                </Button>
            }
        >
            {error && <Alert variant="danger" className="mb-6">{error}</Alert>}

            <StatCard.Group>
                <StatCard 
                    label="Stock Total" 
                    value={stats.totalStock} 
                    icon={<Package size={18} />}
                    accentColor="var(--color-primary)"
                />
                <StatCard 
                    label="Stock Bajo" 
                    value={stats.lowStock} 
                    trend="negative"
                    icon={<TrendingDown size={18} />}
                    accentColor="var(--color-warning)"
                />
                <StatCard 
                    label="Agotados" 
                    value={stats.outOfStock} 
                    icon={<AlertCircle size={18} />}
                    accentColor="var(--color-danger)"
                />
                <StatCard 
                    label="Valor Inventario" 
                    value={`BS. ${stats.inventoryValue.toLocaleString()}`} 
                    icon={<TrendingUp size={18} />}
                    accentColor="var(--color-success)"
                />
            </StatCard.Group>

            <div className={styles.tableWrapper}>
                <div className={styles.toolbar}>
                    <div className={styles.searchBar}>
                        <Search size={18} className={styles.searchIcon} />
                        <input 
                            type="text" 
                            placeholder="Buscar por nombre o SKU..." 
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                </div>

                <DataTable 
                    columns={columns}
                    data={filteredProducts}
                    loading={loading}
                    emptyText="No se encontraron productos en el inventario."
                    footer={`Mostrando ${filteredProducts.length} productos en inventario`}
                />
            </div>

            {/* Modal de Ajuste Manual */}
            {adjustmentModal.open && (
                <div className={styles.overlay} onClick={() => setAdjustmentModal({ open: false, product: null, value: 0 })}>
                    <div className={styles.modal} onClick={e => e.stopPropagation()}>
                        <div className={styles.modalHeader}>
                            <h3>Ajuste de Inventario</h3>
                            <button className={styles.closeBtn} onClick={() => setAdjustmentModal({ open: false, product: null, value: 0 })}>
                                <X size={18} />
                            </button>
                        </div>
                        <div className={styles.modalBody}>
                            <p>Estás ajustando el stock de: <strong>{adjustmentModal.product.nombre}</strong></p>
                            <div className={styles.adjustmentForm}>
                                <div className={styles.formGroup}>
                                    <label>Stock actual: {adjustmentModal.product.stock}</label>
                                    <div className={styles.manualInput}>
                                        <input 
                                            type="number" 
                                            value={adjustmentModal.value} 
                                            onChange={e => setAdjustmentModal(prev => ({ ...prev, value: parseInt(e.target.value) || 0 }))}
                                            min="0"
                                        />
                                        <span className={styles.unitLabel}>unidades</span>
                                    </div>
                                </div>
                            </div>
                            <Alert variant="info">
                                El valor ingresado será el <strong>nuevo stock total</strong> del producto.
                            </Alert>
                        </div>
                        <div className={styles.modalFooter}>
                            <Button 
                                variant="ghost" 
                                onClick={() => setAdjustmentModal({ open: false, product: null, value: 0 })}
                            >
                                Cancelar
                            </Button>
                            <Button 
                                variant="primary" 
                                leftIcon={<Check size={16} />}
                                loading={updatingId === adjustmentModal.product.id}
                                onClick={() => handleStockAdjustment(adjustmentModal.product.id, adjustmentModal.product.stock, adjustmentModal.value, true)}
                            >
                                Aplicar Nuevo Stock
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </AppView>
    );
};

export default InventarioView;
