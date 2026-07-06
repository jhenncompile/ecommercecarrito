import api from 'core/services/api';

/**
 * Servicio de Solicitud de Restock / Intención de Compra (CU-25).
 * Usado por el storefront (cliente) y el dashboard del vendedor.
 */
export const restockApi = {
  // Cliente: registrar interés en un producto agotado
  solicitar: (productoId) => api.post('/restock/', { producto_id: productoId }),

  // Vendedor: ranking de productos más solicitados
  ranking: () => api.get('/restock/ranking/'),
};
