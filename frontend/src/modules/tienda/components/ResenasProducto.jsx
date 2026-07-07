import { useEffect, useState, useCallback } from 'react';
import { Star } from 'lucide-react';
import { resenasApi } from 'modules/tienda/services/resenasApi';

const STAR_COLOR = '#f59e0b';

function Estrellas({ valor, size = 16 }) {
  return (
    <span style={{ display: 'inline-flex', gap: '2px', verticalAlign: 'middle' }}>
      {[0, 1, 2, 3, 4].map((i) => (
        <Star
          key={i}
          size={size}
          color={STAR_COLOR}
          fill={valor >= i + 1 ? STAR_COLOR : 'none'}
        />
      ))}
    </span>
  );
}

function SelectorEstrellas({ valor, onChange, size = 30 }) {
  return (
    <span style={{ display: 'inline-flex', gap: '4px' }}>
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          onClick={() => onChange(n)}
          style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer', lineHeight: 0 }}
          aria-label={`${n} estrellas`}
        >
          <Star size={size} color={STAR_COLOR} fill={valor >= n ? STAR_COLOR : 'none'} />
        </button>
      ))}
    </span>
  );
}

/**
 * Bloque de Reseñas y Calificaciones (CU-27) para el modal de producto.
 * Muestra el promedio, la lista de reseñas y, si el usuario es comprador
 * verificado, un formulario para calificar.
 */
export default function ResenasProducto({ productId, onToast }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [calif, setCalif] = useState(0);
  const [comentario, setComentario] = useState('');
  const [enviando, setEnviando] = useState(false);

  const cargar = useCallback(async () => {
    setLoading(true);
    try {
      const res = await resenasApi.porProducto(productId);
      setData(res.data);
      setCalif(res.data?.mi_resena?.calificacion || 0);
      setComentario(res.data?.mi_resena?.comentario || '');
    } catch {
      setData({ resumen: { promedio: 0, total: 0 }, resenas: [], mi_resena: null, puede_resenar: false });
    } finally {
      setLoading(false);
    }
  }, [productId]);

  useEffect(() => { cargar(); }, [cargar]);

  const enviar = async () => {
    if (calif < 1) {
      onToast?.('Selecciona una calificación (1 a 5 estrellas).', 'info');
      return;
    }
    setEnviando(true);
    try {
      await resenasApi.enviar(productId, calif, comentario.trim());
      onToast?.('¡Gracias por tu reseña!', 'success');
      await cargar();
    } catch (e) {
      const msg = e?.response?.data?.error || 'No se pudo enviar la reseña.';
      onToast?.(msg, 'error');
    } finally {
      setEnviando(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '16px 0', color: '#64748b' }}>Cargando reseñas…</div>;
  }

  const resumen = data?.resumen || { promedio: 0, total: 0 };
  const resenas = data?.resenas || [];
  const puedeResenar = data?.puede_resenar;
  const yaReseno = !!data?.mi_resena;

  return (
    <div style={{ marginTop: '24px', borderTop: '1px solid #e2e8f0', paddingTop: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>Reseñas</h3>
        {resumen.total > 0 && (
          <>
            <Estrellas valor={resumen.promedio} size={18} />
            <span style={{ color: '#64748b', fontWeight: 600 }}>
              {Number(resumen.promedio).toFixed(1)} ({resumen.total})
            </span>
          </>
        )}
      </div>

      {puedeResenar && (
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '14px', padding: '16px', marginBottom: '20px' }}>
          <div style={{ fontWeight: 700, marginBottom: '10px' }}>{yaReseno ? 'Editar tu reseña' : 'Deja tu reseña'}</div>
          <SelectorEstrellas valor={calif} onChange={setCalif} />
          <textarea
            value={comentario}
            onChange={(e) => setComentario(e.target.value)}
            placeholder="Cuéntanos tu experiencia (opcional)"
            rows={3}
            style={{ width: '100%', marginTop: '12px', padding: '10px', borderRadius: '10px', border: '1px solid #cbd5e1', resize: 'vertical', fontFamily: 'inherit', fontSize: '14px' }}
          />
          <button
            type="button"
            onClick={enviar}
            disabled={enviando}
            style={{
              marginTop: '12px', width: '100%', padding: '12px', borderRadius: '10px', border: 'none',
              background: enviando ? '#94a3b8' : '#0f172a', color: '#fff', fontWeight: 700,
              cursor: enviando ? 'default' : 'pointer',
            }}
          >
            {enviando ? 'Enviando…' : (yaReseno ? 'Actualizar reseña' : 'Enviar reseña')}
          </button>
        </div>
      )}

      {resenas.length === 0 ? (
        <div style={{ color: '#64748b' }}>Aún no hay reseñas para este producto.</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {resenas.map((r) => (
            <div key={r.id} style={{ border: '1px solid #e2e8f0', borderRadius: '12px', padding: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px' }}>
                <strong>{r.cliente_nombre}</strong>
                <Estrellas valor={r.calificacion} size={14} />
              </div>
              {r.comentario && <p style={{ margin: '6px 0 0', color: '#334155', lineHeight: 1.4 }}>{r.comentario}</p>}
              {r.created_at && (
                <div style={{ marginTop: '6px', color: '#94a3b8', fontSize: '12px' }}>
                  {String(r.created_at).slice(0, 10)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
