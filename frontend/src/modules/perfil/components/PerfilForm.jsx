import { useState, useEffect } from 'react';
import './PerfilForm.css';

export default function PerfilForm({ perfil, onGuardar, loading }) {
  const role = localStorage.getItem('user_role');
  const isCliente = role === 'cliente';

  const [formData, setFormData] = useState({
    // Campos de Usuario (Vendedor)
    first_name: '',
    last_name: '',
    email: '',
    // Campos de Cliente
    nombre: '',
    correo: '',
    telefono: '',
    nit: '',
    // Común
    password: '',
  });

  useEffect(() => {
    if (perfil) {
      if (isCliente) {
        setFormData({
          nombre: perfil.nombre || '',
          correo: perfil.correo || '',
          telefono: perfil.telefono || '',
          nit: perfil.nit || '',
          password: '',
        });
      } else {
        setFormData({
          first_name: perfil.first_name || '',
          last_name: perfil.last_name || '',
          email: perfil.email || '',
          password: '',
        });
      }
    }
  }, [perfil, isCliente]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const dataToSubmit = { ...formData };
    
    // Eliminar campos vacíos o no pertinentes
    if (!dataToSubmit.password) delete dataToSubmit.password;
    
    // Si es cliente, nos aseguramos de no enviar campos de vendedor y viceversa
    if (isCliente) {
      delete dataToSubmit.first_name;
      delete dataToSubmit.last_name;
      delete dataToSubmit.email;
    } else {
      delete dataToSubmit.nombre;
      delete dataToSubmit.correo;
      delete dataToSubmit.telefono;
      delete dataToSubmit.nit;
    }
    
    onGuardar(dataToSubmit);
  };

  return (
    <form className="perfil-form" onSubmit={handleSubmit}>
      {isCliente ? (
        // VISTA CLIENTE
        <>
          <div className="form-group">
            <label htmlFor="nombre">Nombre Completo</label>
            <input
              type="text"
              id="nombre"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              placeholder="Tu nombre completo"
              disabled={loading}
              required
            />
          </div>
          <div className="form-row">
            <div>
              <label htmlFor="correo">Correo Electrónico</label>
              <input
                type="email"
                id="correo"
                name="correo"
                value={formData.correo}
                onChange={handleChange}
                placeholder="tu@email.com"
                disabled={loading}
                required
              />
            </div>
            <div>
              <label htmlFor="telefono">Teléfono</label>
              <input
                type="text"
                id="telefono"
                name="telefono"
                value={formData.telefono}
                onChange={handleChange}
                placeholder="Ej: 71234567"
                disabled={loading}
              />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="nit">NIT / CI</label>
            <input
              type="text"
              id="nit"
              name="nit"
              value={formData.nit}
              onChange={handleChange}
              placeholder="Número de identificación"
              disabled={loading}
            />
          </div>
        </>
      ) : (
        // VISTA VENDEDOR
        <>
          <div className="form-row">
            <div>
              <label htmlFor="first_name">Nombre</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="Tu nombre"
                disabled={loading}
              />
            </div>
            <div>
              <label htmlFor="last_name">Apellidos</label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Tus apellidos"
                disabled={loading}
              />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="email">Correo Electrónico</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="tu@email.com"
              disabled={loading}
            />
          </div>
        </>
      )}

      <div className="form-group">
        <label htmlFor="password">Nueva Contraseña (opcional)</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Dejar en blanco para no cambiar"
          disabled={loading}
          autoComplete="new-password"
        />
      </div>

      <div className="form-actions">
        <button type="submit" disabled={loading} className="btn-save">
          {loading ? 'Guardando...' : 'Guardar Cambios'}
        </button>
      </div>
    </form>
  );
}
