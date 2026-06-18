// src/modules/recordatorios/hooks/useRecordatorios.js
import { useState, useCallback } from 'react';
import api from 'core/services/api';

/**
 * Hook para gestionar recordatorios (CU-20).
 * Encapsula: listar, crear, editar, eliminar, marcar completado, próximos 7 días.
 */
export function useRecordatorios() {
  const [recordatorios, setRecordatorios] = useState([]);
  const [proximos, setProximos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAll = useCallback(async (filtros = {}) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filtros.tipo) params.append('tipo', filtros.tipo);
      if (filtros.completado !== undefined) params.append('completado', filtros.completado);
      const { data } = await api.get(`/recordatorios/?${params.toString()}`);
      const lista = data.results ?? data;
      setRecordatorios(lista);
      return lista;
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar recordatorios');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchProximos = useCallback(async () => {
    try {
      const { data } = await api.get('/recordatorios/proximos/');
      setProximos(data.results ?? data);
    } catch {
      setProximos([]);
    }
  }, []);

  const crear = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post('/recordatorios/', payload);
      setRecordatorios((prev) => [data, ...prev]);
      return data;
    } catch (err) {
      const msg = err.response?.data
        ? Object.values(err.response.data).flat().join(' ')
        : 'Error al crear recordatorio';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const actualizar = useCallback(async (id, payload) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.patch(`/recordatorios/${id}/`, payload);
      setRecordatorios((prev) => prev.map((r) => (r.id === id ? data : r)));
      return data;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Error al actualizar';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const eliminar = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/recordatorios/${id}/`);
      setRecordatorios((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al eliminar');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const marcarCompletado = useCallback(async (id) => {
    try {
      const { data } = await api.post(`/recordatorios/${id}/marcar-completado/`, {});
      setRecordatorios((prev) => prev.map((r) => (r.id === id ? data : r)));
      return data;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Error al marcar como completado';
      setError(msg);
      throw new Error(msg);
    }
  }, []);

  return {
    recordatorios,
    proximos,
    loading,
    error,
    fetchAll,
    fetchProximos,
    crear,
    actualizar,
    eliminar,
    marcarCompletado,
  };
}
