import api from 'core/services/api';

/**
 * Servicio unificado de Perfil.
 * Detecta el rol del usuario para llamar al endpoint correcto.
 */
export const perfilService = {
  // Obtener datos personales (detecta rol automáticamente)
  obtenerPerfil: async () => {
    const role = localStorage.getItem('user_role'); // 'admin', 'vendedor' o 'cliente'
    const endpoint = (role === 'cliente') 
      ? '/clientes/perfil/' 
      : '/usuarios/perfil/';
      
    const response = await api.get(endpoint);
    return response.data;
  },

  // Actualizar datos personales
  actualizarPerfil: async (datos) => {
    const role = localStorage.getItem('user_role');
    const endpoint = (role === 'cliente') 
      ? '/clientes/perfil/' 
      : '/usuarios/perfil/';

    const response = await api.patch(endpoint, datos);
    return response.data;
  },

  // Gestión de Tienda (Solo para Vendedores)
  obtenerTiendaPerfil: async () => {
    const role = localStorage.getItem('user_role');
    if (role === 'cliente') return null; // Los clientes no tienen perfil de tienda

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