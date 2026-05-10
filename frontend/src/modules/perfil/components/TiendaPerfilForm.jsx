import { useState, useEffect } from 'react';
import { Image as ImageIcon, X } from 'lucide-react';
import './PerfilForm.css';

export default function TiendaPerfilForm({ perfil, onGuardar, loading }) {
  const [formData, setFormData] = useState({
    nombre_comercial: '',
    descripcion: '',
    categoria_tienda: '',
  });
  const [icono, setIcono] = useState(null);
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    if (perfil) {
      setFormData({
        nombre_comercial: perfil.nombre_comercial || '',
        descripcion: perfil.descripcion || '',
        categoria_tienda: perfil.categoria_tienda || '',
      });
      if (perfil.icono) {
        setPreview(perfil.icono);
      }
    }
  }, [perfil]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setIcono(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = new FormData();
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    if (icono) {
      data.append('icono', icono);
    }
    onGuardar(data);
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

      <div className="form-actions" style={{ marginTop: '15px' }}>
        <button type="submit" disabled={loading}>
          {loading ? 'Guardando...' : 'Guardar Datos de Tienda'}
        </button>
      </div>
    </form>
  );
}
