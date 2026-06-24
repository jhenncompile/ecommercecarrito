import React, { createContext, useState, useCallback, useContext, useEffect } from 'react';
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
    const is_superuser = localStorage.getItem('user_is_superuser') === 'true';
    const is_staff     = localStorage.getItem('user_is_staff') === 'true';
    
    let permisos_efectivos = [];
    try {
      const storedPermisos = localStorage.getItem('user_permisos_efectivos');
      if (storedPermisos) permisos_efectivos = JSON.parse(storedPermisos);
    } catch(e) {}
    
    return token ? { fullName: fullName || 'Usuario', token, role, is_superuser, is_staff, permisos_efectivos } : null;
  });

  // Fetch fresco de permisos al montar si hay token
  useEffect(() => {
    if (user?.token) {
      import('core/services/api').then(({ default: api }) => {
        api.get('/usuarios/perfil/')
          .then(res => {
            const permisos = res.data.permisos_efectivos || [];
            localStorage.setItem('user_permisos_efectivos', JSON.stringify(permisos));
            setUser(prev => {
              if (!prev) return null;
              // Si son iguales, no hacemos re-render
              if (JSON.stringify(prev.permisos_efectivos) === JSON.stringify(permisos)) {
                return prev;
              }
              return { ...prev, permisos_efectivos: permisos };
            });
          })
          .catch(() => {});
      });
    }
  }, [user?.token]);

  const login = useCallback((accessToken, refreshToken, fullName, role = 'vendedor', is_superuser = false, is_staff = false) => {
    localStorage.setItem('access_token',  accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user_full_name', fullName || '');
    localStorage.setItem('user_role', role);
    localStorage.setItem('user_is_superuser', is_superuser);
    localStorage.setItem('user_is_staff', is_staff);
    localStorage.removeItem('user_permisos_efectivos'); // Se refrescará en el useEffect
    setUser({ fullName: fullName || 'Usuario', token: accessToken, role, is_superuser, is_staff, permisos_efectivos: [] });
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
      localStorage.removeItem('user_is_superuser');
      localStorage.removeItem('user_is_staff');
      localStorage.removeItem('user_permisos_efectivos');
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
