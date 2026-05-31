import { useState, useCallback } from 'react';
import api from 'core/services/api';

export function usePrediction() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cache, setCache] = useState({});

  const generatePrediction = useCallback(async (config) => {
    const cacheKey = JSON.stringify(config);
    if (cache[cacheKey]) {
      setData(cache[cacheKey]);
      return cache[cacheKey];
    }

    setLoading(true);
    setError(null);
    try {
      const response = await api.post('reportes/prediccion/', config);
      setData(response.data);
      setCache(prev => ({ ...prev, [cacheKey]: response.data }));
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Error generando la predicción');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [cache]);

  return { data, loading, error, generatePrediction };
}
