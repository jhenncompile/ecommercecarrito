import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from 'core/hooks/useAuth';
import { getBaseDomain } from 'core/utils/domain';
import Spinner from 'shared/components/Spinner/Spinner';

export default function SSOReceiverView() {
  const navigate  = useNavigate();
  const location  = useLocation();
  const { login } = useAuth();

  useEffect(() => {
    const params   = new URLSearchParams(location.search);
    const token    = params.get('token');
    const refresh  = params.get('refresh');
    const fullName = params.get('full_name');
    const isSuper  = params.get('is_superuser') === 'true';
    const isStaff  = params.get('is_staff') === 'true';
    const role     = isSuper ? 'admin' : (params.get('role') || 'vendedor');

    if (token) {
      login(token, refresh || '', fullName ? decodeURIComponent(fullName) : '', role, isSuper, isStaff);

      const hostname   = window.location.hostname;
      const baseDomain = getBaseDomain(hostname);

      if (role === 'admin') {
        navigate('/su', { replace: true });
      } else if (role === 'cliente') {
        // Detectar si estamos en un subdominio de tenant:
        //   tienda1.localhost            → !isOnBaseDomain → /catalogo
        //   tienda1.192.168.x.x.nip.io  → !isOnBaseDomain → /catalogo
        //   localhost                    → /mi-portal
        //   192.168.x.x                 → /mi-portal
        const isOnBaseDomain = (hostname === baseDomain) || (hostname === 'localhost');
        if (!isOnBaseDomain) {
          navigate('/catalogo', { replace: true });
        } else {
          navigate('/mi-portal', { replace: true });
        }
      } else {
        // Vendedor: siempre al Dashboard
        navigate('/dashboard', { replace: true });
      }
    } else {
      // Sin token → ir al login del dominio base
      const port = window.location.port ? `:${window.location.port}` : '';
      const base = getBaseDomain(window.location.hostname);
      window.location.href = `${window.location.protocol}//${base}${port}/login`;
    }
  }, [navigate, location, login]);

  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px', background: 'var(--color-bg)' }}>
      <Spinner size="lg" />
      <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)' }}>
        Sincronizando sesión...
      </p>
    </div>
  );
}
