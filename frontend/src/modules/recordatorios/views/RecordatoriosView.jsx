// src/modules/recordatorios/views/RecordatoriosView.jsx
import { useEffect, useState } from 'react';
import {
  Bell, Plus, CheckCircle, Pencil, Trash2,
  Clock, AlertTriangle,
  CreditCard, Tag, Link, ClipboardList, Trash
} from 'lucide-react';
import { useRecordatorios } from '../hooks/useRecordatorios';
import styles from './RecordatoriosView.module.css';

// ── Helpers de tipo ──────────────────────────────────────────
const TIPO_CONFIG = {
  TAREA: {
    label: 'Tarea',
    badgeClass: 'badgeTarea',
    accentClass: 'accentTarea',
    icon: <ClipboardList size={13} />,
  },
  PAGO: {
    label: 'Pago',
    badgeClass: 'badgePago',
    accentClass: 'accentPago',
    icon: <CreditCard size={13} />,
  },
  PROMOCION: {
    label: 'Promocion',
    badgeClass: 'badgePromo',
    accentClass: 'accentPromo',
    icon: <Tag size={13} />,
  },
};

const FILTROS = [
  { value: '', label: 'Todos',       icon: null },
  { value: 'TAREA',    label: 'Tareas',      icon: <ClipboardList size={13} /> },
  { value: 'PAGO',     label: 'Pagos',       icon: <CreditCard size={13} /> },
  { value: 'PROMOCION', label: 'Promociones', icon: <Tag size={13} /> },
];

// ── Formulario vacío ──────────────────────────────────────────
const FORM_EMPTY = {
  titulo: '',
  descripcion: '',
  tipo: 'TAREA',
  fecha_recordatorio: '',
  pedido: '',
};

function formatFecha(fechaStr) {
  if (!fechaStr) return '—';
  const d = new Date(fechaStr);
  return d.toLocaleString('es-BO', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function isVencido(rec) {
  return !rec.completado && new Date(rec.fecha_recordatorio) < new Date();
}

// ── Componente principal ──────────────────────────────────────
export default function RecordatoriosView() {
  const {
    recordatorios, proximos, loading, error,
    fetchAll, fetchProximos, crear, actualizar, eliminar, marcarCompletado,
  } = useRecordatorios();

  const [filtroTipo, setFiltroTipo] = useState('');
  const [tabActiva, setTabActiva] = useState('pendientes'); // 'pendientes' | 'completados'
  const [modalAbierto, setModalAbierto] = useState(false);
  const [editando, setEditando] = useState(null);
  const [form, setForm] = useState(FORM_EMPTY);
  const [guardando, setGuardando] = useState(false);
  const [errModal, setErrModal] = useState('');
  const [confirmEliminar, setConfirmEliminar] = useState(null);

  // Cargar datos al montar
  useEffect(() => {
    fetchAll({ tipo: filtroTipo });
    fetchProximos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroTipo]);

  // ── Lista filtrada ────────────────────────────────────────────
  const lista = recordatorios.filter((r) =>
    tabActiva === 'pendientes' ? !r.completado : r.completado,
  );

  // ── Modal: abrir para crear ───────────────────────────────────
  const abrirCrear = () => {
    setEditando(null);
    setForm(FORM_EMPTY);
    setErrModal('');
    setModalAbierto(true);
  };

  // ── Modal: abrir para editar ──────────────────────────────────
  const abrirEditar = (rec) => {
    setEditando(rec);
    setForm({
      titulo: rec.titulo,
      descripcion: rec.descripcion || '',
      tipo: rec.tipo,
      fecha_recordatorio: rec.fecha_recordatorio
        ? rec.fecha_recordatorio.substring(0, 16)
        : '',
      pedido: rec.pedido ?? '',
    });
    setErrModal('');
    setModalAbierto(true);
  };

  // ── Guardar (crear o editar) ──────────────────────────────────
  const handleGuardar = async () => {
    if (!form.titulo.trim()) { setErrModal('El título es requerido.'); return; }
    if (!form.fecha_recordatorio) { setErrModal('La fecha y hora es requerida.'); return; }

    setGuardando(true);
    setErrModal('');
    try {
      const payload = {
        titulo: form.titulo.trim(),
        descripcion: form.descripcion.trim(),
        tipo: form.tipo,
        fecha_recordatorio: new Date(form.fecha_recordatorio).toISOString(),
        ...(form.pedido ? { pedido: parseInt(form.pedido, 10) } : { pedido: null }),
      };

      if (editando) {
        await actualizar(editando.id, payload);
      } else {
        await crear(payload);
      }
      setModalAbierto(false);
      fetchProximos();
    } catch (e) {
      setErrModal(e.message || 'Error al guardar.');
    } finally {
      setGuardando(false);
    }
  };

  // ── Marcar completado ─────────────────────────────────────────
  const handleCompletar = async (id) => {
    await marcarCompletado(id);
    fetchProximos();
  };

  // ── Eliminar ──────────────────────────────────────────────────
  const handleEliminar = async (id) => {
    await eliminar(id);
    setConfirmEliminar(null);
    fetchProximos();
  };

  // ── Render ────────────────────────────────────────────────────
  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1><Bell size={22} style={{ verticalAlign: 'middle', marginRight: 8 }} />Recordatorios</h1>
          <p>Gestiona tareas, pagos y promociones programadas</p>
        </div>
        <button className={styles.btnNuevo} onClick={abrirCrear}>
          <Plus size={18} /> Nuevo Recordatorio
        </button>
      </div>

      {/* Banner próximos */}
      {proximos.length > 0 && (
        <div className={styles.bannerProximos}>
          <AlertTriangle size={20} />
          <span>
            Tienes <strong>{proximos.length}</strong> recordatorio{proximos.length > 1 ? 's' : ''}{' '}
            pendiente{proximos.length > 1 ? 's' : ''} en los próximos 7 días.
          </span>
        </div>
      )}

      {/* Error global */}
      {error && <div className={styles.errorMsg}>{error}</div>}

      {/* Filtros por tipo */}
      <div className={styles.filtros}>
        {FILTROS.map((f) => (
          <button
            key={f.value}
            className={`${styles.filtroBtn} ${filtroTipo === f.value ? styles.active : ''}`}
            onClick={() => setFiltroTipo(f.value)}
          >
            {f.icon && <span style={{ display: 'inline-flex', verticalAlign: 'middle', marginRight: 4 }}>{f.icon}</span>}
            {f.label}
          </button>
        ))}
      </div>

      {/* Tabs pendientes / completados */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${tabActiva === 'pendientes' ? styles.active : ''}`}
          onClick={() => setTabActiva('pendientes')}
        >
          Pendientes ({recordatorios.filter((r) => !r.completado).length})
        </button>
        <button
          className={`${styles.tab} ${tabActiva === 'completados' ? styles.active : ''}`}
          onClick={() => setTabActiva('completados')}
        >
          Completados ({recordatorios.filter((r) => r.completado).length})
        </button>
      </div>

      {/* Contenido */}
      {loading ? (
        <div className={styles.spinner} />
      ) : lista.length === 0 ? (
        <div className={styles.empty}>
          <Bell size={48} />
          <h3>
            {tabActiva === 'pendientes'
              ? 'No hay recordatorios pendientes'
              : 'No hay recordatorios completados'}
          </h3>
          <p>
            {tabActiva === 'pendientes'
              ? 'Crea un nuevo recordatorio para no olvidar nada importante.'
              : 'Los recordatorios que marques como completados aparecerán aquí.'}
          </p>
        </div>
      ) : (
        <div className={styles.grid}>
          {lista.map((rec) => {
            const cfg = TIPO_CONFIG[rec.tipo] || TIPO_CONFIG.TAREA;
            const vencido = isVencido(rec);
            return (
              <div
                key={rec.id}
                className={`${styles.card} ${rec.completado ? styles.completada : ''}`}
              >
                {/* Acento lateral de color */}
                <div className={`${styles.cardAccent} ${styles[cfg.accentClass]}`} />

                {/* Encabezado */}
                <div className={styles.cardHeader}>
                  <span className={`${styles.cardTitulo} ${rec.completado ? styles.tachado : ''}`}>
                    {rec.titulo}
                  </span>
                  <span className={`${styles.badge} ${styles[cfg.badgeClass]}`}>
                    {cfg.icon}&nbsp;{cfg.label}
                  </span>
                </div>

                {/* Descripción */}
                {rec.descripcion && (
                  <p className={styles.cardDesc}>{rec.descripcion}</p>
                )}

                {/* Fecha */}
                <div className={`${styles.cardFecha} ${vencido ? styles.vencido : ''}`}>
                  {vencido ? <AlertTriangle size={13} /> : <Clock size={13} />}
                  {vencido ? 'Vencido: ' : ''}{formatFecha(rec.fecha_recordatorio)}
                </div>

                {/* Pedido vinculado */}
                {rec.pedido_numero && (
                  <div className={styles.pedidoLink}>
                    <Link size={12} /> Pedido #{rec.pedido_numero}
                  </div>
                )}

                {/* Acciones */}
                {!rec.completado && (
                  <div className={styles.cardFooter}>
                    <button
                      className={`${styles.btnAccion} ${styles.btnCompletar}`}
                      onClick={() => handleCompletar(rec.id)}
                    >
                      <CheckCircle size={13} /> Completar
                    </button>
                    <button
                      className={`${styles.btnAccion} ${styles.btnEditar}`}
                      onClick={() => abrirEditar(rec)}
                    >
                      <Pencil size={13} /> Editar
                    </button>
                    <button
                      className={`${styles.btnAccion} ${styles.btnEliminar}`}
                      onClick={() => setConfirmEliminar(rec.id)}
                    >
                      <Trash2 size={13} /> Eliminar
                    </button>
                  </div>
                )}
                {rec.completado && (
                  <div className={styles.cardFooter}>
                    <button
                      className={`${styles.btnAccion} ${styles.btnEliminar}`}
                      onClick={() => setConfirmEliminar(rec.id)}
                    >
                      <Trash2 size={13} /> Eliminar
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ── Modal crear / editar ───────────────────────────── */}
      {modalAbierto && (
        <div className={styles.modalOverlay} onClick={() => setModalAbierto(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {editando ? <Pencil size={20} /> : <Plus size={20} />}
              {editando ? 'Editar Recordatorio' : 'Nuevo Recordatorio'}
            </h2>

            {errModal && <div className={styles.errorMsg}>{errModal}</div>}

            <div className={styles.formGroup}>
              <label>Título *</label>
              <input
                type="text"
                placeholder="Ej: Pagar proveedor ABC"
                value={form.titulo}
                onChange={(e) => setForm({ ...form, titulo: e.target.value })}
                maxLength={200}
              />
            </div>

            <div className={styles.formGroup}>
              <label>Descripción</label>
              <textarea
                placeholder="Detalles adicionales (opcional)"
                value={form.descripcion}
                onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
              />
            </div>

            <div className={styles.formGroup}>
              <label>Tipo *</label>
              <select
                value={form.tipo}
                onChange={(e) => setForm({ ...form, tipo: e.target.value })}
              >
                <option value="TAREA">Tarea</option>
                <option value="PAGO">Pago</option>
                <option value="PROMOCION">Promocion</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label>Fecha y Hora del Evento *</label>
              <input
                type="datetime-local"
                value={form.fecha_recordatorio}
                onChange={(e) =>
                  setForm({ ...form, fecha_recordatorio: e.target.value })
                }
              />
            </div>

            <div className={styles.formGroup}>
              <label>Vincular a Pedido (ID, opcional)</label>
              <input
                type="number"
                placeholder="Nro. de pedido"
                value={form.pedido}
                onChange={(e) => setForm({ ...form, pedido: e.target.value })}
                min="1"
              />
            </div>

            <div className={styles.modalFooter}>
              <button
                className={styles.btnCancelar}
                onClick={() => setModalAbierto(false)}
              >
                Cancelar
              </button>
              <button
                className={styles.btnGuardar}
                onClick={handleGuardar}
                disabled={guardando}
              >
                {guardando ? 'Guardando…' : editando ? 'Actualizar' : 'Crear Recordatorio'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal confirmar eliminación ─────────────────────── */}
      {confirmEliminar && (
        <div className={styles.modalOverlay} onClick={() => setConfirmEliminar(null)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()} style={{ maxWidth: 380 }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Trash size={20} /> Eliminar Recordatorio</h2>
            <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>
              ¿Estás seguro de que deseas eliminar este recordatorio? Esta acción no se puede deshacer.
            </p>
            <div className={styles.modalFooter}>
              <button className={styles.btnCancelar} onClick={() => setConfirmEliminar(null)}>
                Cancelar
              </button>
              <button
                className={styles.btnGuardar}
                style={{ background: 'linear-gradient(135deg,#ef4444,#dc2626)' }}
                onClick={() => handleEliminar(confirmEliminar)}
              >
                Sí, eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
