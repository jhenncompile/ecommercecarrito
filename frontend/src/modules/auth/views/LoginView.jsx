import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, KeySquare, ArrowRight, Mail } from 'lucide-react';
import AuthLayout from 'shared/layouts/AuthLayout/AuthLayout';
import { Button, Input, Alert } from 'shared/components';
import { useAuth } from 'core/hooks/useAuth';
import api from 'core/services/api';
import styles from './AuthView.module.css';

export default function LoginView() {
  const { login } = useAuth();
  const navigate   = useNavigate();
  const [loginType, setLoginType] = useState('cliente'); // 'cliente' o 'vendedor'
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let endpoint = '';
      let payload = {};

      if (loginType === 'vendedor') {
        // Flujo de Vendedor (Admin)
        endpoint = '/token/';
        payload = { username, password };
      } else {
        // Flujo de Cliente
        endpoint = '/clientes/login/';
        payload = { correo: username, contrasena: password };
      }

      const res = await api.post(endpoint, payload);
      const { access, refresh } = res.data;

      if (loginType === 'vendedor') {
        const { subdomain, full_name } = res.data;
        if (subdomain) {
          const protocol    = window.location.protocol;
          const currentPort = window.location.port;
          const portPart    = (currentPort && currentPort !== '80' && currentPort !== '443')
            ? `:${currentPort}` : '';
          window.location.href = `${protocol}//${subdomain}${portPart}/sso?token=${access}&refresh=${refresh}&full_name=${encodeURIComponent(full_name || '')}`;
        } else {
          login(access, refresh, res.data.full_name, 'vendedor');
          navigate('/dashboard', { replace: true });
        }
      } else {
        // Cliente: Guardar tokens y redirigir a su portal
        login(access, refresh, res.data.cliente?.nombre, 'cliente');
        navigate('/mi-portal', { replace: true });
      }
    } catch {
      setError(loginType === 'vendedor' 
        ? 'Credenciales incorrectas o problema de conexión.'
        : 'Correo o contraseña incorrectos.'
      );
    } finally {
      setLoading(false);
    }
  };

  const isCliente = loginType === 'cliente';

  return (
    <AuthLayout
      headline={<>Bienvenido de nuevo</>}
      subheadline={isCliente 
        ? "Inicia sesión para acceder a tu cuenta de comprador"
        : "Revisa predicciones, gestiona pedidos y atiende clientes desde un solo lugar."
      }
    >
      <div className={styles.formWrap}>
        <div className={styles.formHeader}>
          <h1 className={styles.formTitle}>Iniciar Sesión</h1>
          <p className={styles.formSubtitle}>
            {isCliente ? 'Accede a tu cuenta como cliente' : 'Accede a tu tienda MiQhatu'}
          </p>
        </div>

        {/* Toggle selector para tipo de login */}
        <div style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '24px',
          backgroundColor: '#f3f4f6',
          padding: '4px',
          borderRadius: '8px',
          width: '100%'
        }}>
          <button
            type="button"
            onClick={() => {
              setLoginType('cliente');
              setError('');
            }}
            style={{
              flex: 1,
              padding: '10px 16px',
              border: 'none',
              borderRadius: '6px',
              backgroundColor: loginType === 'cliente' ? '#ffffff' : 'transparent',
              color: loginType === 'cliente' ? '#000' : '#666',
              fontWeight: loginType === 'cliente' ? '600' : '500',
              fontSize: '14px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: loginType === 'cliente' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
            }}
          >
            Soy Cliente
          </button>
          <button
            type="button"
            onClick={() => {
              setLoginType('vendedor');
              setError('');
            }}
            style={{
              flex: 1,
              padding: '10px 16px',
              border: 'none',
              borderRadius: '6px',
              backgroundColor: loginType === 'vendedor' ? '#ffffff' : 'transparent',
              color: loginType === 'vendedor' ? '#000' : '#666',
              fontWeight: loginType === 'vendedor' ? '600' : '500',
              fontSize: '14px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: loginType === 'vendedor' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
            }}
          >
            Soy Vendedor
          </button>
        </div>

        {error && <Alert variant="danger">{error}</Alert>}

        <form onSubmit={handleLogin} className={styles.form}>
          <Input
            id="login-username"
            label={isCliente ? "Correo Electrónico" : "Usuario"}
            leftIcon={isCliente ? <Mail size={16} /> : <User size={16} />}
            type={isCliente ? "email" : "text"}
            placeholder={isCliente ? "tu@correo.com" : "Tu nombre de usuario"}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoFocus
          />
          <Input
            id="login-password"
            label="Contraseña"
            leftIcon={<KeySquare size={16} />}
            type="password"
            placeholder="••••••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            labelRight={
              !isCliente && (
                <Link to="/forgot-password" className={styles.forgotLink}>
                  ¿Olvidaste tu contraseña?
                </Link>
              )
            }
          />
          <Button
            type="submit"
            fullWidth
            loading={loading}
            rightIcon={<ArrowRight size={16} />}
            style={{ marginTop: '8px' }}
          >
            Entrar
          </Button>
        </form>

        <p className={styles.footer}>
          ¿No tienes cuenta?{' '}
          <Link to={isCliente ? "/registro-cliente" : "/crear-tienda"}>
            {isCliente ? 'Regístrate aquí' : 'Créala gratis aquí'}
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
}
