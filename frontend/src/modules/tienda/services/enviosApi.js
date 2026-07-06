import api from 'core/services/api';

/**
 * Servicio de Logística y Envíos (CU-24).
 * Fuente única para la configuración de envíos del storefront y la
 * gestión de zonas de delivery del vendedor.
 */
export const enviosApi = {
  // Storefront: ciudad de la tienda + flags + zonas activas
  obtenerConfig: () => api.get('/envios/config/'),

  // Vendedor: CRUD de zonas de delivery
  listarZonas: () => api.get('/zonas-delivery/'),
  crearZona: (data) => api.post('/zonas-delivery/', data),
  actualizarZona: (id, data) => api.patch(`/zonas-delivery/${id}/`, data),
  eliminarZona: (id) => api.delete(`/zonas-delivery/${id}/`),
};
