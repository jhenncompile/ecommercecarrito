import { useState, useEffect, useCallback } from 'react';
import { Image as ImageIcon, X, MapPin, Trash2, Plus } from 'lucide-react';
import { enviosApi } from 'modules/tienda/services/enviosApi';
import './PerfilForm.css';

export default function TiendaPerfilForm({ perfil, onGuardar, loading }) {
  const [formData, setFormData] = useState({
    nombre_comercial: '',
    descripcion: '',
    categoria_tienda: '',
    ciudad: '',
    whatsapp: '',
    enable_local_delivery: false,
    enable_national_shipping: true,
  });
  const [icono, setIcono] = useState(null);
  const [preview, setPreview] = useState(null);

  // --- Zonas de Delivery (CU-24) ---
  const [zonas, setZonas] = useState([]);
  const [nuevaZona, setNuevaZona] = useState({ zone_name: '', price: '' });
  const [zonasLoading, setZonasLoading] = useState(false);

  // --- Estado de guardado y validación ---
  const [guardando, setGuardando] = useState(false);
  const [feedback, setFeedback] = useState(null); // { tipo: 'success' | 'error', texto }

  useEffect(() => {
    if (perfil) {
      setFormData({
        nombre_comercial: perfil.nombre_comercial || '',
        descripcion: perfil.descripcion || '',
        categoria_tienda: perfil.categoria_tienda || '',
        ciudad: perfil.ciudad || '',
        whatsapp: perfil.whatsapp || '',
        enable_local_delivery: !!perfil.enable_local_delivery,
        enable_national_shipping: perfil.enable_national_shipping !== false,
      });
      if (perfil.icono) {
        setPreview(perfil.icono);
      }
    }
  }, [perfil]);

  const cargarZonas = useCallback(async () => {
    try {
      const res = await enviosApi.listarZonas();
      setZonas(Array.isArray(res.data) ? res.data : res.data?.results || []);
    } catch (e) {
      setZonas([]);
    }
  }, []);

  useEffect(() => { cargarZonas(); }, [cargarZonas]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    // Limpiar feedback al editar cualquier campo
    if (feedback) setFeedback(null);
  };

  // Valida los datos antes de enviar. Devuelve un mensaje de error o null si es válido.
  const validar = () => {
    if (!formData.nombre_comercial.trim()) {
      return 'El nombre comercial es obligatorio.';
    }
    if (!formData.enable_local_delivery && !formData.enable_national_shipping) {
      return 'Debes habilitar al menos un método de entrega (delivery local o envío nacional).';
    }
    if (formData.enable_local_delivery && zonas.length === 0) {
      return 'Para habilitar el delivery local debes agregar al menos una zona de delivery.';
    }
    return null;
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setIcono(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const errorValidacion = validar();
    if (errorValidacion) {
      setFeedback({ tipo: 'error', texto: errorValidacion });
      return;
    }

    const data = new FormData();
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    if (icono) {
      data.append('icono', icono);
    }

    setGuardando(true);
    setFeedback(null);
    try {
      const resultado = await onGuardar(data);
      if (!resultado || resultado.success) {
        setFeedback({ tipo: 'success', texto: 'Datos de la tienda guardados correctamente.' });
      } else {
        setFeedback({ tipo: 'error', texto: resultado.error || 'No se pudieron guardar los datos.' });
      }
    } catch (err) {
      setFeedback({ tipo: 'error', texto: 'Ocurrió un error al guardar los datos.' });
    } finally {
      setGuardando(false);
    }
  };

  const handleAgregarZona = async () => {
    if (!nuevaZona.zone_name.trim()) return;
    setZonasLoading(true);
    try {
      await enviosApi.crearZona({
        zone_name: nuevaZona.zone_name.trim(),
        price: parseFloat(nuevaZona.price) || 0,
      });
      setNuevaZona({ zone_name: '', price: '' });
      await cargarZonas();
    } catch (e) {
      // no romper el flujo del formulario
    } finally {
      setZonasLoading(false);
    }
  };

  const handleEliminarZona = async (id) => {
    setZonasLoading(true);
    try {
      await enviosApi.eliminarZona(id);
      await cargarZonas();
    } catch (e) {
      // ignorar
    } finally {
      setZonasLoading(false);
    }
  };

  return (
    <form className="perfil-form" onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
      <h3 style={{ marginBottom: '15px', color: '#0f172a' }}>Datos de la Tienda</h3>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Icono de la Tienda</label>
        {!preview ? (
          <div style={{
            border: '2px dashed #cbd5e1', borderRadius: '12px', padding: '20px',
            textAlign: 'center', cursor: 'pointer', backgroundColor: '#f8fafc', maxWidth: '200px'
          }}>
            <label style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <ImageIcon size={32} color="#94a3b8" />
              <span style={{ marginTop: '8px', color: '#64748b', fontSize: '14px' }}>Subir icono</span>
              <input type="file" accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} disabled={loading} />
            </label>
          </div>
        ) : (
          <div style={{ position: 'relative', display: 'inline-block', border: '1px solid #e2e8f0', borderRadius: '12px', overflow: 'hidden' }}>
            <img src={preview} alt="Preview" style={{ width: '100px', height: '100px', objectFit: 'cover' }} />
            <button
              type="button"
              onClick={() => { setIcono(null); setPreview(null); }}
              style={{ position: 'absolute', top: '4px', right: '4px', background: 'rgba(0,0,0,0.5)', color: '#fff', border: 'none', borderRadius: '50%', padding: '4px', cursor: 'pointer' }}
              disabled={loading}
            >
              <X size={14} />
            </button>
          </div>
        )}
      </div>

      <div className="form-row">
        <div>
          <label htmlFor="nombre_comercial">Nombre Comercial</label>
          <input
            type="text"
            id="nombre_comercial"
            name="nombre_comercial"
            value={formData.nombre_comercial}
            onChange={handleChange}
            placeholder="Nombre de tu negocio"
            disabled={loading}
          />
        </div>
        <div>
          <label htmlFor="categoria_tienda">Categoría</label>
          <input
            type="text"
            id="categoria_tienda"
            name="categoria_tienda"
            value={formData.categoria_tienda}
            onChange={handleChange}
            placeholder="Ej: Ropa, Tecnología..."
            disabled={loading}
          />
        </div>
      </div>

      <div>
        <label htmlFor="descripcion">Descripción</label>
        <textarea
          id="descripcion"
          name="descripcion"
          value={formData.descripcion}
          onChange={handleChange}
          placeholder="Describe tu tienda..."
          disabled={loading}
          rows={3}
          style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
        />
      </div>

      {/* --- Logística y Envíos (CU-24) --- */}
      <h3 style={{ margin: '24px 0 15px', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <MapPin size={18} /> Logística y Envíos
      </h3>

      <div className="form-row">
        <div>
          <label htmlFor="ciudad">Ciudad de la Tienda</label>
          <input
            type="text"
            id="ciudad"
            name="ciudad"
            value={formData.ciudad}
            onChange={handleChange}
            placeholder="Ej: Santa Cruz"
            disabled={loading}
          />
        </div>
        <div>
          <label htmlFor="whatsapp">WhatsApp de la Tienda</label>
          <input
            type="text"
            id="whatsapp"
            name="whatsapp"
            value={formData.whatsapp}
            onChange={handleChange}
            placeholder="Ej: 59170012345 (con código de país)"
            disabled={loading}
          />
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', margin: '10px 0 4px' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'normal', cursor: 'pointer' }}>
          <input
            type="checkbox"
            name="enable_local_delivery"
            checked={formData.enable_local_delivery}
            onChange={handleChange}
            disabled={loading}
          />
          Habilitar Delivery Local (por zonas)
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'normal', cursor: 'pointer' }}>
          <input
            type="checkbox"
            name="enable_national_shipping"
            checked={formData.enable_national_shipping}
            onChange={handleChange}
            disabled={loading}
          />
          Habilitar Envío Nacional (Encomienda, pago en destino)
        </label>
      </div>

      {/* Gestor de zonas de delivery */}
      <div style={{ marginTop: '16px', padding: '14px', border: '1px solid #e2e8f0', borderRadius: '10px', backgroundColor: '#f8fafc' }}>
        <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Zonas de Delivery</label>

        {zonas.length === 0 ? (
          <p style={{ color: '#64748b', fontSize: '14px', margin: '0 0 10px' }}>Aún no has agregado zonas de delivery.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '12px' }}>
            {zonas.map(z => (
              <div key={z.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '8px 12px' }}>
                <span style={{ fontSize: '14px', color: '#0f172a' }}>{z.zone_name}</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <strong style={{ fontSize: '14px' }}>Bs. {parseFloat(z.price).toFixed(2)}</strong>
                  <button
                    type="button"
                    onClick={() => handleEliminarZona(z.id)}
                    disabled={zonasLoading}
                    style={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer', display: 'flex' }}
                    title="Eliminar zona"
                  >
                    <Trash2 size={16} />
                  </button>
                </span>
              </div>
            ))}
          </div>
        )}

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <input
            type="text"
            value={nuevaZona.zone_name}
            onChange={(e) => setNuevaZona(prev => ({ ...prev, zone_name: e.target.value }))}
            placeholder="Nombre de la zona"
            disabled={zonasLoading}
            style={{ flex: 2, padding: '8px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
          />
          <input
            type="number"
            min="0"
            step="0.01"
            value={nuevaZona.price}
            onChange={(e) => setNuevaZona(prev => ({ ...prev, price: e.target.value }))}
            placeholder="Precio Bs."
            disabled={zonasLoading}
            style={{ flex: 1, padding: '8px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
          />
          <button
            type="button"
            onClick={handleAgregarZona}
            disabled={zonasLoading || !nuevaZona.zone_name.trim()}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', borderRadius: '8px', border: 'none', background: '#0f172a', color: '#fff', cursor: 'pointer', whiteSpace: 'nowrap' }}
          >
            <Plus size={16} /> Agregar
          </button>
        </div>
      </div>

      {feedback && (
        <div
          role="status"
          style={{
            marginTop: '18px',
            padding: '12px 14px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 600,
            border: '1px solid',
            backgroundColor: feedback.tipo === 'success' ? '#dcfce7' : '#fee2e2',
            borderColor: feedback.tipo === 'success' ? '#86efac' : '#fca5a5',
            color: feedback.tipo === 'success' ? '#166534' : '#991b1b',
          }}
        >
          {feedback.texto}
        </div>
      )}

      <div className="form-actions" style={{ marginTop: '15px', alignItems: 'center' }}>
        <button type="submit" disabled={guardando || loading}>
          {guardando ? 'Guardando...' : 'Guardar Datos de Tienda'}
        </button>
      </div>
    </form>
  );
}
