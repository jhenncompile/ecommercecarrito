import { useAuth } from 'core/hooks/useAuth';

export default function MarketplaceView() {
  const { user } = useAuth();
  
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundColor: 'var(--color-bg)',
      flexDirection: 'column',
      gap: '16px'
    }}>
      <h1 style={{
        fontSize: '32px',
        fontWeight: '600',
        color: 'var(--color-text)',
        margin: 0
      }}>
        Bienvenido {user?.name || 'Cliente'}
      </h1>
    </div>
  );
}
