import api from 'core/services/api';

// Nota: cambio temporal para pruebas (forzar host público localhost)
export const perfilService = {
  // Obtener datos del vendedor actual
  obtenerPerfil: async () => {
    // Usar URL absoluta en localhost para evitar resolución por subdominios
    const token = localStorage.getItem('access_token');
    const response = await api.get('http://localhost:8001/api/usuarios/perfil/', {
      headers: { Authorization: token ? `Bearer ${token}` : undefined },
    });
    return response.data;
  },

  // Actualizar datos personales
  actualizarPerfil: async (datos) => {
    const token = localStorage.getItem('access_token');
    const response = await api.patch('http://localhost:8001/api/usuarios/perfil/', datos, {
      headers: { Authorization: token ? `Bearer ${token}` : undefined },
    });
    return response.data;
  },

  obtenerTiendaPerfil: async () => {
    const response = await api.get('/tienda/perfil/');
    return response.data;
  },

  actualizarTiendaPerfil: async (formData) => {
    const response = await api.patch('/tienda/perfil/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};