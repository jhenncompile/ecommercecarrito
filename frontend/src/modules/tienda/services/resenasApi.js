import api from 'core/services/api';

/**
 * Servicio de Reseñas y Calificaciones (CU-27).
 * Usado por el storefront (cliente) y el panel del vendedor.
 */
export const resenasApi = {
  // Público: resumen + lista de reseñas de un producto (incluye mi_resena y puede_resenar si hay sesión)
  porProducto: (productoId) => api.get(`/resenas/producto/${productoId}/`),

  // Cliente comprador: crear o actualizar reseña
  enviar: (productoId, calificacion, comentario = '') =>
    api.post('/resenas/', { producto_id: productoId, calificacion, comentario }),

  // Vendedor: todas las reseñas de la tienda
  listar: () => api.get('/resenas/'),
};
