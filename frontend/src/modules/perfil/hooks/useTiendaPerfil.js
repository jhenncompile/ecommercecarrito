import { useState, useEffect, useCallback } from 'react';
import { perfilService } from '../services/perfilService';

export const useTiendaPerfil = () => {
  const [tiendaPerfil, setTiendaPerfil] = useState(null);
  const [loadingTienda, setLoadingTienda] = useState(true);
  const [errorTienda, setErrorTienda] = useState(null);

  useEffect(() => {
    const cargarTienda = async () => {
      try {
        setLoadingTienda(true);
        const datos = await perfilService.obtenerTiendaPerfil();
        setTiendaPerfil(datos);
      } catch (err) {
        setErrorTienda(err.response?.data?.detail || 'Error al cargar perfil de la tienda');
      } finally {
        setLoadingTienda(false);
      }
    };

    cargarTienda();
  }, []);

  const actualizarTienda = useCallback(async (datos) => {
    try {
      const actualizado = await perfilService.actualizarTiendaPerfil(datos);
      setTiendaPerfil(actualizado);
      return { success: true };
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al actualizar tienda';
      setErrorTienda(errorMsg);
      return { success: false, error: errorMsg };
    }
  }, []);

  return { tiendaPerfil, loadingTienda, errorTienda, actualizarTienda };
};
