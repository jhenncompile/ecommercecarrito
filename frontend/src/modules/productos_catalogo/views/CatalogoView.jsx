/**
 * productos_catalogo/views/CatalogoView.jsx
 * Vista previa del catálogo — perspectiva del vendedor.
 */
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutGrid, List, Search, X, Tag, ImageOff,
  Pencil, Trash2, ChevronRight, Package, ArrowLeft,
  ShoppingBag, Layers,
} from 'lucide-react';
import { Button, Input, Badge, Alert, Spinner } from 'shared/components';
import { productosApi, categoriasApi } from '../services/productosApi';
import styles from './Productos.module.css';
import catStyles from './CatalogoView.module.css';

// ─── Constantes ─────────────────────────────────────────────────
const EMPTY_PRODUCT = {
  nombre: '', sku: '', descripcion: '', precio: '',
  stock: '', categoria: '', imagen_url: '', activo: true,
};

// ─── Helpers ────────────────────────────────────────────────────
function buildTree(cats) {
  const map = {};
  cats.forEach((c) => { map[c.id] = { ...c, children: [] }; });
  const roots = [];
  cats.forEach((c) => {
    if (c.parent && map[c.parent]) map[c.parent].children.push(map[c.id]);
    else roots.push(map[c.id]);
  });
  return roots;
}

function calcDescuento(precio, promo) {
  if (!promo?.descuento_pct) return null;
  const pct = parseFloat(promo.descuento_pct);
  const original = parseFloat(precio);
  const final = original * (1 - pct / 100);
  return { pct, final: final.toFixed(2), original: original.toFixed(2) };
}

function stockVariant(stock) {
  if (stock === 0) return { label: 'Sin stock', cls: catStyles.stockEmpty };
  if (stock < 5)  return { label: `¡Solo ${stock}!`, cls: catStyles.stockLow };
  return { label: `${stock} en stock`, cls: catStyles.stockOk };
}

// ─── ProductDrawer ───────────────────────────────────────────────
function ProductDrawer({ open, producto, categorias, onClose, onSaved }) {
  const isEdit = !!producto?.id;
  const [form,    setForm]    = useState(EMPTY_PRODUCT);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  useEffect(() => {
    if (open) {
      setForm(producto
        ? {
            nombre:      producto.nombre      || '',
            sku:         producto.sku         || '',
            descripcion: producto.descripcion || '',
            precio:      producto.precio      || '',
            stock:       producto.stock       ?? '',
            categoria:   producto.categoria   || '',
            imagen_url:  producto.imagen_url  || '',
            activo:      producto.activo      ?? true,
          }
        : EMPTY_PRODUCT
      );
      setError('');
    }
  }, [open, producto]);

  const handle = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((p) => ({ ...p, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.categoria) { setError('Selecciona una categoría.'); return; }
    setLoading(true);
    setError('');
    try {
      const payload = {
        ...form,
        precio: parseFloat(form.precio) || 0,
        stock:  parseInt(form.stock, 10) || 0,
        categoria: parseInt(form.categoria, 10),
      };
      if (isEdit) await productosApi.actualizar(producto.id, payload);
      else        await productosApi.crear(payload);
      onSaved();
      onClose();
    } catch (err) {
      const detail = err.response?.data;
      setError(typeof detail === 'string' ? detail : JSON.stringify(detail) || 'Error al guardar.');
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  const treeOptions = [];
  const padres = categorias.filter((c) => !c.parent && c.activo);
  padres.forEach((p) => {
    treeOptions.push({ value: p.id, label: p.nombre, indent: false });
    categorias
      .filter((c) => c.parent === p.id && c.activo)
      .forEach((s) => treeOptions.push({ value: s.id, label: `↳ ${s.nombre}`, indent: true }));
  });
  categorias
    .filter((c) => c.parent && c.activo && !padres.find((p) => p.id === c.parent))
    .forEach((s) => treeOptions.push({ value: s.id, label: s.nombre, indent: false }));

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={styles.drawer}>
        <div className={styles.drawerHeader}>
          <span className={styles.drawerTitle}>{isEdit ? 'Editar Producto' : 'Nuevo Producto'}</span>
          <button className={styles.drawerClose} onClick={onClose}><X size={18} /></button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'contents' }}>
          <div className={styles.drawerBody}>
            {error && <Alert variant="danger">{error}</Alert>}

            <div className={styles.section}>
              <span className={styles.sectionLabel}><Package size={13} /> Datos del Producto</span>
              <Input id="cv-nombre" name="nombre" label="Nombre *" placeholder="Nombre del producto" value={form.nombre} onChange={handle} required />
              <div className={styles.twoCol}>
                <Input id="cv-sku" name="sku" label="SKU" placeholder="COD-001" value={form.sku} onChange={handle} />
                <div>
                  <label htmlFor="cv-categoria" style={{ display: 'flex', gap: 6, alignItems: 'center', fontSize: 'var(--text-sm)', fontWeight: 'var(--font-medium)', color: 'var(--color-text-secondary)', marginBottom: 8 }}>
                    <Tag size={14} /> Categoría *
                  </label>
                  <select id="cv-categoria" name="categoria" className={styles.select} value={form.categoria} onChange={handle} required>
                    <option value="">Seleccionar...</option>
                    {treeOptions.map((opt) => (
                      <option key={opt.value} value={opt.value} style={{ paddingLeft: opt.indent ? 24 : 0 }}>{opt.label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label htmlFor="cv-desc" style={{ display: 'block', fontSize: 'var(--text-sm)', fontWeight: 'var(--font-medium)', color: 'var(--color-text-secondary)', marginBottom: 8 }}>Descripción</label>
                <textarea id="cv-desc" name="descripcion" rows={3} placeholder="Descripción del producto..." value={form.descripcion} onChange={handle}
                  style={{ width: '100%', padding: 'var(--space-3) var(--space-4)', background: 'var(--color-surface-2)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', color: 'var(--color-text)', fontFamily: 'var(--font-sans)', fontSize: 'var(--text-sm)', resize: 'vertical', minHeight: 80, outline: 'none' }}
                  onFocus={(e) => { e.target.style.borderColor = 'var(--color-primary)'; e.target.style.boxShadow = '0 0 0 3px var(--color-primary-ghost)'; }}
                  onBlur={(e) => { e.target.style.borderColor = ''; e.target.style.boxShadow = ''; }}
                />
              </div>
            </div>

            <div className={styles.section}>
              <span className={styles.sectionLabel}>Precio & Inventario</span>
              <div className={styles.twoCol}>
                <Input id="cv-precio" name="precio" label="Precio (BS.) *" type="number" min="0" step="0.01" placeholder="0.00" value={form.precio} onChange={handle} required />
                <Input id="cv-stock" name="stock" label="Stock *" type="number" min="0" placeholder="0" value={form.stock} onChange={handle} required />
              </div>
            </div>

            <div className={styles.section}>
              <span className={styles.sectionLabel}>Imagen</span>
              <Input id="cv-imagen" name="imagen_url" label="URL de imagen" type="url" placeholder="https://..." value={form.imagen_url} onChange={handle} />
              {form.imagen_url && (
                <img src={form.imagen_url} alt="preview" style={{ width: '100%', maxHeight: 160, objectFit: 'cover', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }} onError={(e) => { e.target.style.display = 'none'; }} />
              )}
            </div>

            <div className={styles.section}>
              <span className={styles.sectionLabel}>Estado</span>
              <div className={styles.toggleRow}>
                <span className={styles.toggleLabel}>Producto activo</span>
                <label className={styles.toggle}>
                  <input type="checkbox" name="activo" checked={form.activo} onChange={handle} />
                  <span className={styles.toggleSlider} />
                </label>
              </div>
            </div>
          </div>

          <div className={styles.drawerFooter}>
            <Button variant="ghost" type="button" onClick={onClose}>Cancelar</Button>
            <Button type="submit" loading={loading}>{isEdit ? 'Guardar cambios' : 'Crear producto'}</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Sidebar ─────────────────────────────────────────────────────
function Sidebar({ categorias, selectedId, onSelect }) {
  const tree = buildTree(categorias.filter((c) => c.activo));
  const [openNodes, setOpenNodes] = useState({});
  const toggle = (id) => setOpenNodes((p) => ({ ...p, [id]: !p[id] }));

  return (
    <aside className={catStyles.sidebar}>
      <div className={catStyles.sidebarHeader}>
        <span className={catStyles.sidebarTitle}>
          <Layers size={13} style={{ display: 'inline', marginRight: 6 }} />
          Categorías
        </span>
      </div>
      <nav className={catStyles.catList}>
        <button className={`${catStyles.catBtn} ${!selectedId ? catStyles.active : ''}`} onClick={() => onSelect(null)}>
          <Package size={14} /><span style={{ flex: 1 }}>Todos los productos</span>
        </button>
        {tree.map((node) => (
          <div key={node.id}>
            <button
              className={`${catStyles.catBtn} ${selectedId === node.id ? catStyles.active : ''}`}
              onClick={() => { onSelect(selectedId === node.id ? null : node.id); if (node.children.length) toggle(node.id); }}
            >
              <Tag size={13} /><span style={{ flex: 1 }}>{node.nombre}</span>
              {node.children.length > 0 && (
                <ChevronRight size={13} style={{ transition: 'transform 0.2s', transform: openNodes[node.id] ? 'rotate(90deg)' : 'none', color: 'var(--color-text-muted)' }} />
              )}
            </button>
            {openNodes[node.id] && node.children.map((sub) => (
              <button key={sub.id} className={`${catStyles.catBtn} ${catStyles.subCatBtn} ${selectedId === sub.id ? catStyles.active : ''}`} onClick={() => onSelect(selectedId === sub.id ? null : sub.id)}>
                <span style={{ flex: 1 }}>{sub.nombre}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>
    </aside>
  );
}

// ─── Tarjeta grid ───────────────────────────────────────────────
function ProductCard({ producto, categorias, onEdit, onDelete }) {
  const cat = categorias.find((c) => c.id === producto.categoria);
  const descuento = calcDescuento(producto.precio, producto.promocion_detail);
  const stock = stockVariant(producto.stock);

  return (
    <article className={catStyles.card}>
      <div className={catStyles.imgWrap}>
        {producto.imagen_url
          ? <img src={producto.imagen_url} alt={producto.nombre} className={catStyles.img} onError={(e) => { e.target.style.display = 'none'; }} />
          : <div className={catStyles.imgPlaceholder}><ImageOff size={28} /><span>Sin imagen</span></div>
        }
        <div className={catStyles.badges}>
          {descuento && <span className={catStyles.badgePromo}>-{descuento.pct}%</span>}
          {!producto.activo && <span className={catStyles.badgeInactive}>Inactivo</span>}
        </div>
        <div className={catStyles.cardActions}>
          <button className={catStyles.actionBtn} onClick={() => onEdit(producto)}><Pencil size={14} /></button>
          <button className={`${catStyles.actionBtn} ${catStyles.danger}`} onClick={() => onDelete(producto)}><Trash2 size={14} /></button>
        </div>
      </div>
      <div className={catStyles.cardBody}>
        {cat && <span className={catStyles.catTag}><Tag size={10} /> {cat.nombre}</span>}
        <p className={catStyles.productName}>{producto.nombre}</p>
        {producto.sku && <p className={catStyles.productSku}>SKU: {producto.sku}</p>}
        <div className={catStyles.priceRow}>
          {descuento
            ? <><span className={catStyles.price}>Bs. {descuento.final}</span><span className={catStyles.priceOriginal}>Bs. {descuento.original}</span></>
            : <span className={catStyles.price}>Bs. {parseFloat(producto.precio).toFixed(2)}</span>
          }
        </div>
        <div className={catStyles.stockRow}>
          <span className={`${catStyles.stockBadge} ${stock.cls}`}>{stock.label}</span>
        </div>
      </div>
    </article>
  );
}

// ─── Fila lista ─────────────────────────────────────────────────
function ProductRow({ producto, categorias, onEdit, onDelete }) {
  const cat = categorias.find((c) => c.id === producto.categoria);
  const descuento = calcDescuento(producto.precio, producto.promocion_detail);
  const stock = stockVariant(producto.stock);

  return (
    <div className={catStyles.listCard}>
      {producto.imagen_url
        ? <img src={producto.imagen_url} alt={producto.nombre} className={catStyles.listImg} onError={(e) => { e.target.style.display = 'none'; }} />
        : <div className={catStyles.listImgPlaceholder}><ImageOff size={20} /></div>
      }
      <div className={catStyles.listInfo}>
        <p className={catStyles.listName}>{producto.nombre}</p>
        <p className={catStyles.listMeta}>{producto.sku && `SKU: ${producto.sku}`}{producto.sku && cat && ' · '}{cat && cat.nombre}</p>
      </div>
      <div className={catStyles.listRight}>
        <span className={`${catStyles.stockBadge} ${stock.cls}`}>{stock.label}</span>
        {descuento && <Badge variant="danger">-{descuento.pct}%</Badge>}
        <span className={catStyles.listPrice}>{descuento ? `Bs. ${descuento.final}` : `Bs. ${parseFloat(producto.precio).toFixed(2)}`}</span>
        <div className={catStyles.listActions}>
          <button className={catStyles.actionBtn} onClick={() => onEdit(producto)}><Pencil size={14} /></button>
          <button className={`${catStyles.actionBtn} ${catStyles.danger}`} onClick={() => onDelete(producto)}><Trash2 size={14} /></button>
        </div>
      </div>
    </div>
  );
}

// ─── Vista principal ────────────────────────────────────────────
export default function CatalogoView() {
  const navigate = useNavigate();
  const [productos,    setProductos]    = useState([]);
  const [categorias,   setCategorias]   = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState('');
  const [search,       setSearch]       = useState('');
  const [selectedCat,  setSelectedCat]  = useState(null);
  const [viewMode,     setViewMode]     = useState('grid');
  const [sortBy,       setSortBy]       = useState('nombre');
  const [drawerOpen,   setDrawerOpen]   = useState(false);
  const [editProduct,  setEditProduct]  = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting,     setDeleting]     = useState(false);

  const cargar = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [pRes, cRes] = await Promise.all([productosApi.listar(), categoriasApi.listar()]);
      const lista = (r) => Array.isArray(r.data) ? r.data : r.data?.results ?? [];
      setProductos(lista(pRes));
      setCategorias(lista(cRes));
    } catch {
      setError('No se pudieron cargar los datos.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  const filtrados = productos
    .filter((p) => {
      const matchSearch = !search
        || p.nombre?.toLowerCase().includes(search.toLowerCase())
        || p.sku?.toLowerCase().includes(search.toLowerCase());
      const matchCat = !selectedCat || (() => {
        if (p.categoria === selectedCat) return true;
        return categorias.filter((c) => c.parent === selectedCat).map((c) => c.id).includes(p.categoria);
      })();
      return matchSearch && matchCat;
    })
    .sort((a, b) => {
      if (sortBy === 'precio_asc')  return parseFloat(a.precio) - parseFloat(b.precio);
      if (sortBy === 'precio_desc') return parseFloat(b.precio) - parseFloat(a.precio);
      if (sortBy === 'stock')       return b.stock - a.stock;
      return a.nombre.localeCompare(b.nombre);
    });

  const handleDelete = async (prod) => {
    if (deleteTarget?.id !== prod.id) { setDeleteTarget(prod); return; }
    setDeleting(true);
    try {
      await productosApi.eliminar(prod.id);
      setDeleteTarget(null);
      cargar();
    } catch {
      alert('No se pudo eliminar el producto.');
    } finally {
      setDeleting(false);
    }
  };

  const handleEdit = (prod) => { setEditProduct(prod); setDrawerOpen(true); };
  const catNombre = selectedCat ? categorias.find((c) => c.id === selectedCat)?.nombre : null;

  return (
     <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-6)' }}>
        <div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: 0 }}>
            Vista Previa del Catálogo
          </h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)', margin: 0 }}>
            Así verán tus clientes los productos
          </p>
        </div>
        <Button variant="ghost" leftIcon={<ArrowLeft size={15} />} onClick={() => navigate(-1)}>
          Volver a gestión
        </Button>
      </div>
      {error && <Alert variant="danger">{error}</Alert>}

      {deleteTarget && (
        <Alert variant="warning" title={`¿Eliminar "${deleteTarget.nombre}"?`}>
          <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-3)' }}>
            <Button size="sm" variant="danger" loading={deleting} onClick={() => handleDelete(deleteTarget)}>Eliminar</Button>
            <Button size="sm" variant="ghost" onClick={() => setDeleteTarget(null)}>Cancelar</Button>
          </div>
        </Alert>
      )}

      <div className={catStyles.page}>
        <Sidebar categorias={categorias} selectedId={selectedCat} onSelect={setSelectedCat} />

        <div className={catStyles.main}>
          <div className={catStyles.toolbar}>
            <div className={catStyles.searchBox}>
              <Search size={15} style={{ color: 'var(--color-text-muted)', flexShrink: 0 }} />
              <input placeholder="Buscar por nombre o SKU..." value={search} onChange={(e) => setSearch(e.target.value)} />
              {search && (
                <button onClick={() => setSearch('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', display: 'flex', padding: 0 }}>
                  <X size={14} />
                </button>
              )}
            </div>

            <select className={catStyles.sortSelect} value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="nombre">Nombre A-Z</option>
              <option value="precio_asc">Menor precio</option>
              <option value="precio_desc">Mayor precio</option>
              <option value="stock">Mayor stock</option>
            </select>

            <div className={catStyles.viewToggle}>
              <button className={`${catStyles.viewBtn} ${viewMode === 'grid' ? catStyles.active : ''}`} onClick={() => setViewMode('grid')}><LayoutGrid size={15} /></button>
              <button className={`${catStyles.viewBtn} ${viewMode === 'list' ? catStyles.active : ''}`} onClick={() => setViewMode('list')}><List size={15} /></button>
            </div>
          </div>

          <div className={catStyles.resultsBar}>
            <div className={catStyles.breadcrumb}>
              <button className={catStyles.breadcrumbLink} onClick={() => setSelectedCat(null)}>Todos</button>
              {catNombre && <><ChevronRight size={13} /><span style={{ color: 'var(--color-text)' }}>{catNombre}</span></>}
            </div>
            <span>{loading ? 'Cargando...' : `${filtrados.length} producto${filtrados.length !== 1 ? 's' : ''}`}</span>
          </div>

          {loading && <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--space-12)' }}><Spinner /></div>}

          {!loading && viewMode === 'grid' && (
            <div className={catStyles.grid}>
              {filtrados.length === 0
                ? <div className={catStyles.empty}><ShoppingBag size={40} style={{ opacity: 0.3 }} /><p className={catStyles.emptyTitle}>No se encontraron productos</p></div>
                : filtrados.map((p) => <ProductCard key={p.id} producto={p} categorias={categorias} onEdit={handleEdit} onDelete={handleDelete} />)
              }
            </div>
          )}

          {!loading && viewMode === 'list' && (
            <div className={catStyles.list}>
              {filtrados.length === 0
                ? <div className={catStyles.empty}><ShoppingBag size={40} style={{ opacity: 0.3 }} /><p className={catStyles.emptyTitle}>No se encontraron productos</p></div>
                : filtrados.map((p) => <ProductRow key={p.id} producto={p} categorias={categorias} onEdit={handleEdit} onDelete={handleDelete} />)
              }
            </div>
          )}
        </div>
      </div>

      <ProductDrawer open={drawerOpen} producto={editProduct} categorias={categorias} onClose={() => setDrawerOpen(false)} onSaved={cargar} />
    </div>   
  );
}