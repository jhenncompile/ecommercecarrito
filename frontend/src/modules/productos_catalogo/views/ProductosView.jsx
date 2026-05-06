import { useState, useEffect, useCallback } from 'react';
import {
  Plus, Search, RefreshCw, Tag, Package, ChevronRight,
  X, Pencil, Trash2, ImageOff, FolderPlus, Layers, Eye
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AppView   from 'shared/widgets/AppView/AppView';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Button, Input, Badge, Alert, Spinner } from 'shared/components';
import { productosApi, categoriasApi } from '../services/productosApi';
import styles from './Productos.module.css';

// ─── Utilidades ────────────────────────────────────────────────
const EMPTY_PRODUCT = {
  nombre: '', sku: '', descripcion: '', precio: '',
  stock: '', categoria: '', imagen_url: '', activo: true,
};
const EMPTY_CAT = { nombre: '', descripcion: '', parent: '' };

/**
 * Convierte la lista plana de categorías en un árbol padre → hijos.
 * Devuelve solo las raíces (parent === null).
 */
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

// ─── Sub-componentes ────────────────────────────────────────────

/** Nodo del árbol de categorías */
function CatNode({ node, selectedId, onSelect, depth = 0 }) {
  const [open, setOpen] = useState(false);
  const hasSubs = node.children?.length > 0;
  const isSelected = selectedId === node.id;

  return (
    <>
      <div
        className={`${styles.catItem} ${isSelected ? styles.selected : ''}`}
        style={{ paddingLeft: `${12 + depth * 16}px` }}
        onClick={() => onSelect(isSelected ? null : node.id)}
      >
        {hasSubs ? (
          <ChevronRight
            size={14}
            className={`${styles.catChevron} ${open ? styles.open : ''}`}
            onClick={(e) => { e.stopPropagation(); setOpen(!open); }}
          />
        ) : (
          <span style={{ width: 14, display: 'inline-block' }} />
        )}
        <Tag size={13} />
        <span style={{ flex: 1, fontSize: 'var(--text-sm)' }}>{node.nombre}</span>
        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
          {node.children?.length > 0 && `(${node.children.length})`}
        </span>
      </div>

      {hasSubs && open && node.children.map((child) => (
        <CatNode
          key={child.id}
          node={child}
          selectedId={selectedId}
          onSelect={onSelect}
          depth={depth + 1}
        />
      ))}
    </>
  );
}

/** Panel lateral de árbol de categorías */
function CategoryPanel({ categorias, selectedId, onSelect, onManage }) {
  const tree = buildTree(categorias.filter((c) => c.activo));

  return (
    <div className={styles.catPanel}>
      <div className={styles.catPanelHeader}>
        <span className={styles.catPanelTitle}>
          <Layers size={14} style={{ display: 'inline', marginRight: 6 }} />
          Categorías
        </span>
        <button
          className={styles.iconAction}
          onClick={onManage}
          title="Gestionar categorías"
        >
          <FolderPlus size={14} />
        </button>
      </div>

      <div className={styles.catTree}>
        <div
          className={`${styles.catItem} ${!selectedId ? styles.selected : ''}`}
          onClick={() => onSelect(null)}
          style={{ paddingLeft: 12 }}
        >
          <Package size={13} />
          <span style={{ flex: 1 }}>Todos los productos</span>
        </div>

        {tree.map((node) => (
          <CatNode
            key={node.id}
            node={node}
            selectedId={selectedId}
            onSelect={onSelect}
          />
        ))}
      </div>
    </div>
  );
}

/** Drawer de formulario para crear / editar producto */
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
        stock:  parseInt(form.stock,  10) || 0,
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

  // Construir opciones de select agrupadas (padres → hijos)
  const treeOptions = [];
  const padres = categorias.filter((c) => !c.parent && c.activo);
  padres.forEach((p) => {
    treeOptions.push({ value: p.id, label: p.nombre, indent: false });
    categorias
      .filter((c) => c.parent === p.id && c.activo)
      .forEach((s) => treeOptions.push({ value: s.id, label: `↳ ${s.nombre}`, indent: true }));
  });
  // Subcategorías huérfanas de padres inactivos
  categorias
    .filter((c) => c.parent && c.activo && !padres.find((p) => p.id === c.parent))
    .forEach((s) => treeOptions.push({ value: s.id, label: s.nombre, indent: false }));

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={styles.drawer}>
        <div className={styles.drawerHeader}>
          <span className={styles.drawerTitle}>
            {isEdit ? 'Editar Producto' : 'Nuevo Producto'}
          </span>
          <button className={styles.drawerClose} onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'contents' }}>
          <div className={styles.drawerBody}>
            {error && <Alert variant="danger">{error}</Alert>}

            {/* Datos básicos */}
            <div className={styles.section}>
              <span className={styles.sectionLabel}><Package size={13} /> Datos del Producto</span>

              <Input
                id="prod-nombre"
                name="nombre"
                label="Nombre *"
                placeholder="Nombre del producto"
                value={form.nombre}
                onChange={handle}
                required
              />

              <div className={styles.twoCol}>
                <Input
                  id="prod-sku"
                  name="sku"
                  label="SKU"
                  placeholder="COD-001"
                  value={form.sku}
                  onChange={handle}
                />
                <div>
                  <label
                    htmlFor="prod-categoria"
                    style={{ display: 'flex', gap: 6, alignItems: 'center', fontSize: 'var(--text-sm)', fontWeight: 'var(--font-medium)', color: 'var(--color-text-secondary)', marginBottom: 8 }}
                  >
                    <Tag size={14} /> Categoría *
                  </label>
                  <select
                    id="prod-categoria"
                    name="categoria"
                    className={styles.select}
                    value={form.categoria}
                    onChange={handle}
                    required
                  >
                    <option value="">Seleccionar...</option>
                    {treeOptions.map((opt) => (
                      <option
                        key={opt.value}
                        value={opt.value}
                        style={{ paddingLeft: opt.indent ? 24 : 0 }}
                      >
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label
                  htmlFor="prod-desc"
                  style={{ display: 'block', fontSize: 'var(--text-sm)', fontWeight: 'var(--font-medium)', color: 'var(--color-text-secondary)', marginBottom: 8 }}
                >
                  Descripción
                </label>
                <textarea
                  id="prod-desc"
                  name="descripcion"
                  rows={3}
                  placeholder="Descripción del producto..."
                  value={form.descripcion}
                  onChange={handle}
                  style={{
                    width: '100%',
                    padding: 'var(--space-3) var(--space-4)',
                    background: 'var(--color-surface-2)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                    fontFamily: 'var(--font-sans)',
                    fontSize: 'var(--text-sm)',
                    resize: 'vertical',
                    minHeight: 80,
                    transition: 'border-color var(--transition-fast)',
                    outline: 'none',
                  }}
                  onFocus={(e) => { e.target.style.borderColor = 'var(--color-primary)'; e.target.style.boxShadow = '0 0 0 3px var(--color-primary-ghost)'; }}
                  onBlur={(e)  => { e.target.style.borderColor = ''; e.target.style.boxShadow = ''; }}
                />
              </div>
            </div>

            {/* Precio y Stock */}
            <div className={styles.section}>
              <span className={styles.sectionLabel}>Precio & Inventario</span>
              <div className={styles.twoCol}>
                <Input
                  id="prod-precio"
                  name="precio"
                  label="Precio (BS.) *"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  value={form.precio}
                  onChange={handle}
                  required
                />
                <Input
                  id="prod-stock"
                  name="stock"
                  label="Stock *"
                  type="number"
                  min="0"
                  placeholder="0"
                  value={form.stock}
                  onChange={handle}
                  required
                />
              </div>
            </div>

            {/* Imagen */}
            <div className={styles.section}>
              <span className={styles.sectionLabel}>Imagen</span>
              <Input
                id="prod-imagen"
                name="imagen_url"
                label="URL de imagen"
                type="url"
                placeholder="https://..."
                value={form.imagen_url}
                onChange={handle}
              />
              {form.imagen_url && (
                <img
                  src={form.imagen_url}
                  alt="preview"
                  style={{ width: '100%', maxHeight: 160, objectFit: 'cover', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
              )}
            </div>

            {/* Estado */}
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
            <Button type="submit" loading={loading}>
              {isEdit ? 'Guardar cambios' : 'Crear producto'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

/** Modal para gestionar categorías (crear/ eliminar padres e hijos) */
function CategoryManager({ open, categorias, onClose, onRefresh }) {
  const [form,         setForm]         = useState(EMPTY_CAT);
  const [saving,       setSaving]       = useState(false);
  const [formError,    setFormError]    = useState('');
  const [deletingId,   setDeletingId]   = useState(null);
  const [confirmId,    setConfirmId]    = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((p) => ({ ...p, [name]: value }));
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.nombre.trim()) { setFormError('El nombre es requerido.'); return; }
    setSaving(true);
    setFormError('');
    try {
      await categoriasApi.crear({
        nombre:      form.nombre.trim(),
        descripcion: form.descripcion.trim(),
        parent:      form.parent ? parseInt(form.parent, 10) : null,
      });
      setForm(EMPTY_CAT);
      onRefresh();
    } catch (err) {
      setFormError(JSON.stringify(err.response?.data) || 'Error al crear categoría.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (confirmId !== id) { setConfirmId(id); return; }
    setDeletingId(id);
    try {
      await categoriasApi.eliminar(id);
      onRefresh();
    } catch {
      alert('No se puede eliminar: tiene productos o subcategorías asignadas.');
    } finally {
      setDeletingId(null);
      setConfirmId(null);
    }
  };

  if (!open) return null;

  const padres = categorias.filter((c) => !c.parent);

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={styles.drawer}>
        <div className={styles.drawerHeader}>
          <span className={styles.drawerTitle}>Gestionar Categorías</span>
          <button className={styles.drawerClose} onClick={onClose}><X size={18} /></button>
        </div>

        <div className={styles.drawerBody}>
          {/* Form nueva categoría */}
          <div className={styles.section}>
            <span className={styles.sectionLabel}><Plus size={13} /> Nueva Categoría</span>

            {formError && <Alert variant="danger">{formError}</Alert>}

            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <Input
                id="cat-nombre"
                name="nombre"
                label="Nombre *"
                placeholder="Nombre de la categoría"
                value={form.nombre}
                onChange={handleChange}
              />

              <div>
                <label
                  htmlFor="cat-parent"
                  style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 'var(--text-sm)', fontWeight: 'var(--font-medium)', color: 'var(--color-text-secondary)', marginBottom: 8 }}
                >
                  <Layers size={14} /> Categoría padre (opcional)
                </label>
                <select
                  id="cat-parent"
                  name="parent"
                  className={styles.select}
                  value={form.parent}
                  onChange={handleChange}
                >
                  <option value="">— Sin padre (categoría raíz) —</option>
                  {padres.map((p) => (
                    <option key={p.id} value={p.id}>{p.nombre}</option>
                  ))}
                </select>
              </div>

              <Input
                id="cat-desc"
                name="descripcion"
                label="Descripción"
                placeholder="Descripción corta..."
                value={form.descripcion}
                onChange={handleChange}
              />

              <Button type="submit" loading={saving} leftIcon={<Plus size={15} />}>
                Crear categoría
              </Button>
            </form>
          </div>

          {/* Lista de categorías existentes */}
          <div className={styles.section}>
            <span className={styles.sectionLabel}>Categorías existentes</span>
            <div className={styles.catManagerList}>
              {padres.map((padre) => (
                <div key={padre.id}>
                  <div className={styles.catManagerItem}>
                    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minWidth: 0 }}>
                      <span className={styles.catName}>{padre.nombre}</span>
                      {padre.descripcion && <span className={styles.catDesc}>{padre.descripcion}</span>}
                    </div>
                    {confirmId === padre.id ? (
                      <div className={styles.deleteConfirm}>
                        <span>¿Confirmar?</span>
                        <button className={`${styles.iconAction} ${styles.danger}`} onClick={() => handleDelete(padre.id)}>
                          {deletingId === padre.id ? <Spinner size="sm" /> : <Trash2 size={13} />}
                        </button>
                        <button className={styles.iconAction} onClick={() => setConfirmId(null)}><X size={13} /></button>
                      </div>
                    ) : (
                      <button className={`${styles.iconAction} ${styles.danger}`} onClick={() => handleDelete(padre.id)}>
                        <Trash2 size={13} />
                      </button>
                    )}
                  </div>

                  {/* Subcategorías */}
                  {categorias.filter((c) => c.parent === padre.id).map((sub) => (
                    <div key={sub.id} className={`${styles.catManagerItem} ${styles.sub}`}>
                      <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginRight: 4 }}>↳</span>
                      <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minWidth: 0 }}>
                        <span className={styles.catName} style={{ fontSize: 'var(--text-sm)' }}>{sub.nombre}</span>
                        {sub.descripcion && <span className={styles.catDesc}>{sub.descripcion}</span>}
                      </div>
                      {confirmId === sub.id ? (
                        <div className={styles.deleteConfirm}>
                          <span>¿Confirmar?</span>
                          <button className={`${styles.iconAction} ${styles.danger}`} onClick={() => handleDelete(sub.id)}>
                            {deletingId === sub.id ? <Spinner size="sm" /> : <Trash2 size={13} />}
                          </button>
                          <button className={styles.iconAction} onClick={() => setConfirmId(null)}><X size={13} /></button>
                        </div>
                      ) : (
                        <button className={`${styles.iconAction} ${styles.danger}`} onClick={() => handleDelete(sub.id)}>
                          <Trash2 size={13} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              ))}

              {padres.length === 0 && (
                <p style={{ textAlign: 'center', padding: 'var(--space-6)', color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)' }}>
                  No hay categorías creadas aún.
                </p>
              )}
            </div>
          </div>
        </div>

        <div className={styles.drawerFooter}>
          <Button variant="secondary" onClick={onClose}>Cerrar</Button>
        </div>
      </div>
    </div>
  );
}

// ─── Columnas de la DataTable ──────────────────────────────────
function buildColumns(onEdit, onDelete) {
  return [
    {
      key: 'nombre',
      label: 'Producto',
      render: (val, row) => (
        <div className={styles.productCell}>
          {row.imagen_url
            ? <img src={row.imagen_url} alt={val} className={styles.productImg} onError={(e) => { e.target.style.display = 'none'; }} />
            : <div className={styles.productImgPlaceholder}><ImageOff size={14} /></div>
          }
          <div>
            <p className={styles.productName}>{val}</p>
            {row.sku && <p className={styles.productSku}>SKU: {row.sku}</p>}
          </div>
        </div>
      ),
    },
    {
      key: 'categoria_detail',
      label: 'Categoría',
      render: (val) => val
        ? <Badge variant="primary">{val.ruta_completa || val.nombre}</Badge>
        : <span style={{ color: 'var(--color-text-muted)' }}>—</span>,
    },
    {
      key: 'precio',
      label: 'Precio',
      render: (val) => <strong style={{ color: 'var(--color-text)' }}>BS. {parseFloat(val).toFixed(2)}</strong>,
    },
    {
      key: 'stock',
      label: 'Stock',
      align: 'center',
      render: (val) => (
        <Badge variant={val < 5 ? 'danger' : val < 15 ? 'warning' : 'success'} dot>
          {val} un.
        </Badge>
      ),
    },
    {
      key: 'activo',
      label: 'Estado',
      align: 'center',
      render: (val) => <Badge variant={val ? 'success' : 'default'}>{val ? 'Activo' : 'Inactivo'}</Badge>,
    },
    {
      key: 'id',
      label: '',
      align: 'right',
      render: (val, row) => (
        <div className={styles.rowActions}>
          <button className={styles.iconAction} onClick={() => onEdit(row)} title="Editar">
            <Pencil size={14} />
          </button>
          <button className={`${styles.iconAction} ${styles.danger}`} onClick={() => onDelete(row)} title="Eliminar">
            <Trash2 size={14} />
          </button>
        </div>
      ),
    },
  ];
}

// ─── Vista principal ────────────────────────────────────────────
export default function ProductosView() {
  const navigate = useNavigate(); // ← hook dentro del componente

  const [productos,    setProductos]    = useState([]);
  const [categorias,   setCategorias]   = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState('');
  const [search,       setSearch]       = useState('');
  const [selectedCat,  setSelectedCat]  = useState(null);
  const [drawerOpen,   setDrawerOpen]   = useState(false);
  const [editProduct,  setEditProduct]  = useState(null);
  const [catMgrOpen,   setCatMgrOpen]   = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting,     setDeleting]     = useState(false);

  // Cargar datos
  const cargar = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [pRes, cRes] = await Promise.all([
        productosApi.listar(),
        categoriasApi.listar(),
      ]);
      const obtenerLista = (r) => Array.isArray(r.data) ? r.data : r.data?.results ?? [];
      setProductos(obtenerLista(pRes));
      setCategorias(obtenerLista(cRes));
    } catch {
      setError('No se pudieron cargar los datos. Verifica la conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  // Eliminar producto
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

  // Abrir form edición
  const handleEdit = (prod) => {
    setEditProduct(prod);
    setDrawerOpen(true);
  };

  // Filtrar productos
  const productosFiltrados = productos.filter((p) => {
    const matchSearch = !search
      || p.nombre?.toLowerCase().includes(search.toLowerCase())
      || p.sku?.toLowerCase().includes(search.toLowerCase());

    const matchCat = !selectedCat || (() => {
      if (p.categoria === selectedCat) return true;
      const sub = categorias.filter((c) => c.parent === selectedCat).map((c) => c.id);
      return sub.includes(p.categoria);
    })();

    return matchSearch && matchCat;
  });

  // Nombre de la categoría seleccionada (para el breadcrumb)
  const catSelNombre = selectedCat
    ? categorias.find((c) => c.id === selectedCat)?.nombre
    : null;

  const columns = buildColumns(
    (prod) => handleEdit(prod),
    (prod) => handleDelete(prod),
  );

  return (
    <AppView
      title="Productos & Catálogo"
      subtitle={catSelNombre
        ? `Mostrando productos de: ${catSelNombre}`
        : `${productosFiltrados.length} producto${productosFiltrados.length !== 1 ? 's' : ''} registrados`
      }
      actions={
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          {/* ── NUEVO: botón vista previa ── */}
          <Button
            variant="ghost"
            leftIcon={<Eye size={15} />}
            onClick={() => navigate('/productos/catalogo')}
          >
            Vista previa
          </Button>

          <Button
            variant="secondary"
            leftIcon={<RefreshCw size={15} />}
            onClick={cargar}
            disabled={loading}
          >
            Actualizar
          </Button>
          <Button
            leftIcon={<Plus size={15} />}
            onClick={() => { setEditProduct(null); setDrawerOpen(true); }}
          >
            Nuevo Producto
          </Button>
        </div>
      }
    >
      {error && <Alert variant="danger">{error}</Alert>}

      {/* Confirmación de borrado */}
      {deleteTarget && (
        <Alert variant="warning" title={`¿Eliminar "${deleteTarget.nombre}"?`}>
          <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-3)' }}>
            <Button size="sm" variant="danger" loading={deleting} onClick={() => handleDelete(deleteTarget)}>
              Eliminar
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setDeleteTarget(null)}>Cancelar</Button>
          </div>
        </Alert>
      )}

      {/* Layout: árbol de categorías + tabla */}
      <div className={styles.layout}>
        {/* Panel izquierdo: árbol de categorías */}
        <CategoryPanel
          categorias={categorias}
          selectedId={selectedCat}
          onSelect={setSelectedCat}
          onManage={() => setCatMgrOpen(true)}
        />

        {/* Tabla de productos */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {/* Barra de búsqueda */}
          <div className={styles.toolbar}>
            <div className={styles.toolbarLeft}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
                background: 'var(--color-surface)', border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)', padding: 'var(--space-2) var(--space-4)',
                flex: 1, maxWidth: 340,
                transition: 'border-color var(--transition-fast)',
              }}>
                <Search size={15} style={{ color: 'var(--color-text-muted)', flexShrink: 0 }} />
                <input
                  type="text"
                  placeholder="Buscar por nombre o SKU..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  style={{ background: 'none', border: 'none', outline: 'none', color: 'var(--color-text)', fontSize: 'var(--text-sm)', width: '100%' }}
                />
                {search && (
                  <button onClick={() => setSearch('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', display: 'flex', padding: 0 }}>
                    <X size={14} />
                  </button>
                )}
              </div>
            </div>
          </div>

          <DataTable
            title={catSelNombre ? `Categoría: ${catSelNombre}` : 'Todos los Productos'}
            columns={columns}
            data={productosFiltrados}
            loading={loading}
            emptyText={search
              ? `No se encontraron productos con "${search}"`
              : selectedCat
                ? 'No hay productos en esta categoría.'
                : 'Aún no hay productos. ¡Crea el primero!'
            }
            footer={`${productosFiltrados.length} resultado${productosFiltrados.length !== 1 ? 's' : ''}`}
          />
        </div>
      </div>

      {/* Drawer: crear / editar producto */}
      <ProductDrawer
        open={drawerOpen}
        producto={editProduct}
        categorias={categorias}
        onClose={() => setDrawerOpen(false)}
        onSaved={cargar}
      />

      {/* Drawer: gestionar categorías */}
      <CategoryManager
        open={catMgrOpen}
        categorias={categorias}
        onClose={() => setCatMgrOpen(false)}
        onRefresh={cargar}
      />
    </AppView>
  );
}