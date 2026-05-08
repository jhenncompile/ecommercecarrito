import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Mail, Phone, KeySquare, FileText, ArrowRight } from 'lucide-react';
import AuthLayout from 'shared/layouts/AuthLayout/AuthLayout';
import { Button, Input, Alert } from 'shared/components';
import { useAuth } from 'core/hooks/useAuth';
import api from 'core/services/api';
import styles from './AuthView.module.css';

export default function RegistroView() {
  const { login } = useAuth();
  const navigate = useNavigate();
  
  // Estados para Registro de Cliente
  const [nombre, setNombre] = useState('');
  const [correo, setCorreo] = useState('');
  const [telefono, setTelefono] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [nit, setNit] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRegistro = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // 1. Registro del cliente
      const registroPayload = {
        nombre,
        correo,
        telefono: telefono || null,
        contrasena,
        nit: nit || null,
      };

      const registroRes = await api.post('/clientes/', registroPayload);
      
      if (registroRes.status === 201) {
        setSuccess('¡Registro exitoso! Iniciando sesión automáticamente...');

        // 2. Auto-login con los mismos datos
        try {
          const loginRes = await api.post('/clientes/login/', {
            correo,
            contrasena,
          });

          const { access, refresh } = loginRes.data;
          const clienteNombre = loginRes.data.cliente?.nombre;

          // 3. Guardar tokens en localStorage y contexto
          localStorage.setItem('access_token', access);
          localStorage.setItem('refresh_token', refresh);
          login(access, refresh, clienteNombre);

          // 4. Redirigir al marketplace
          setTimeout(() => {
            navigate('/marketplace', { replace: true });
          }, 1000);
        } catch (loginError) {
          console.error('Error en auto-login:', loginError);
          // Si falla auto-login, redirigir a login para que lo haga manualmente
          setTimeout(() => {
            navigate('/login', { replace: true });
          }, 2000);
        }
      }
    } catch (err) {
      const errorMsg = err.response?.data?.correo?.[0] 
        || err.response?.data?.non_field_errors?.[0]
        || err.response?.data?.detail
        || 'Error en el registro. Por favor, intenta de nuevo.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      headline={<>Bienvenido al Marketplace</>}
      subheadline="Crea tu cuenta para empezar a comprar en nuestras tiendas"
    >
      <div className={styles.formWrap}>
        <div className={styles.formHeader}>
          <h1 className={styles.formTitle}>Registro de Comprador</h1>
          <p className={styles.formSubtitle}>Crea tu cuenta para empezar a comprar</p>
        </div>

        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}

        <form onSubmit={handleRegistro} className={styles.form}>
          <Input
            id="registro-nombre"
            label="Nombre Completo"
            leftIcon={<User size={16} />}
            type="text"
            placeholder="Juan Pérez García"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
            autoFocus
          />

          <Input
            id="registro-correo"
            label="Correo Electrónico"
            leftIcon={<Mail size={16} />}
            type="email"
            placeholder="tu@correo.com"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
          />

          <Input
            id="registro-telefono"
            label="Teléfono"
            leftIcon={<Phone size={16} />}
            type="tel"
            placeholder="+591 71234567"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
          />

          <Input
            id="registro-nit"
            label="NIT"
            leftIcon={<FileText size={16} />}
            type="text"
            placeholder="1234567890"
            value={nit}
            onChange={(e) => setNit(e.target.value)}
          />

          <Input
            id="registro-contrasena"
            label="Contraseña"
            leftIcon={<KeySquare size={16} />}
            type="password"
            placeholder="••••••••••••"
            value={contrasena}
            onChange={(e) => setContrasena(e.target.value)}
            required
          />

          <Button
            type="submit"
            fullWidth
            loading={loading}
            rightIcon={<ArrowRight size={16} />}
            style={{ marginTop: '8px' }}
          >
            Crear Cuenta
          </Button>
        </form>

        <p className={styles.footer}>
          ¿Ya tienes cuenta?{' '}
          <Link to="/login">Inicia sesión aquí</Link>
        </p>
      </div>
    </AuthLayout>
  );
}
