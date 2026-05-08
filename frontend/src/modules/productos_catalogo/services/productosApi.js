/**
 * productos_catalogo/services/productosApi.js
 * Capa de acceso a datos para Productos y Categorías.
 * Centraliza todos los endpoints en un solo lugar.
 */
import api from 'core/services/api';

const BASE_PROD = '/productos';
const BASE_CAT  = '/categorias';

// ─── PRODUCTOS ────────────────────────────────────────────────
export const productosApi = {
  listar:   (params)    => api.get(BASE_PROD + '/', { params }),
  obtener:  (id)        => api.get(`${BASE_PROD}/${id}/`),
  crear:    (data)      => api.post(BASE_PROD + '/', data),
  actualizar: (id, data)=> api.put(`${BASE_PROD}/${id}/`, data),
  parchear:   (id, data)=> api.patch(`${BASE_PROD}/${id}/`, data),
  eliminar: (id)        => api.delete(`${BASE_PROD}/${id}/`),
  
  // Helpers específicos
  ajustarStock: (id, cantidad) => api.patch(`${BASE_PROD}/${id}/`, { stock: cantidad }),
};

// ─── CATEGORÍAS ───────────────────────────────────────────────
export const categoriasApi = {
  listar:   (params)    => api.get(BASE_CAT + '/', { params }),
  obtener:  (id)        => api.get(`${BASE_CAT}/${id}/`),
  crear:    (data)      => api.post(BASE_CAT + '/', data),
  actualizar: (id, data)=> api.put(`${BASE_CAT}/${id}/`, data),
  eliminar: (id)        => api.delete(`${BASE_CAT}/${id}/`),
};
