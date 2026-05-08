import React, { createContext, useState, useCallback, useContext } from 'react';
import { getBaseDomain } from 'core/utils/domain';

// ─── Contexto ────────────────────────────────────────────────
export const AuthContext = createContext(null);

// ─── Provider ────────────────────────────────────────────────
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    // Rehidratar desde localStorage al cargar
    const fullName = localStorage.getItem('user_full_name');
    const token    = localStorage.getItem('access_token');
    const role     = localStorage.getItem('user_role');
    return token ? { fullName: fullName || 'Usuario', token, role } : null;
  });

  const login = useCallback((accessToken, refreshToken, fullName, role = 'vendedor') => {
    localStorage.setItem('access_token',  accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user_full_name', fullName || '');
    localStorage.setItem('user_role', role);
    setUser({ fullName: fullName || 'Usuario', token: accessToken, role });
  }, []);

  const logout = useCallback(async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        // Importación dinámica para evitar ciclo de imports
        const { default: api } = await import('core/services/api');
        await api.post('/logout/', { refresh });
      }
    } catch (_) {
      // Silenciar errores de red en logout
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_full_name');
      localStorage.removeItem('user_role');
      setUser(null);
      const baseDomain = getBaseDomain(window.location.hostname);
      const port = window.location.port ? `:${window.location.port}` : '';
      window.location.href = `${window.location.protocol}//${baseDomain}${port}/login`;
    }
  }, []);

  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

// ─── Hook rápido (también disponible en core/hooks/useAuth) ──
export const useAuthContext = () => useContext(AuthContext);
