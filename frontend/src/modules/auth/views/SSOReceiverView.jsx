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
    const role     = params.get('role') || 'vendedor';

    if (token) {
      login(token, refresh || '', fullName ? decodeURIComponent(fullName) : '', role);
      
      const hostname = window.location.hostname;
      const baseDomain = getBaseDomain(hostname);
      
      // Si es cliente y está en un subdominio, va al catálogo.
      // Si es vendedor/admin, siempre va al dashboard (su panel de control).
      if (role === 'cliente') {
        if (hostname !== baseDomain && hostname !== 'localhost') {
          navigate('/catalogo', { replace: true });
        } else {
          navigate('/mi-portal', { replace: true });
        }
      } else {
        // Vendedor o Admin: Siempre al Dashboard
        navigate('/dashboard', { replace: true });
      }
    } else {
      const baseDomain = getBaseDomain(window.location.hostname);
      const port = window.location.port ? `:${window.location.port}` : '';
      window.location.href = `${window.location.protocol}//${baseDomain}${port}/login`;
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
