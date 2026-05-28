import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import {
  Store, User, Mail, Lock, Globe, Building, CheckCircle2,
  ArrowRight, Sparkles, ShieldCheck, Zap, Image as ImageIcon, X, CreditCard
} from 'lucide-react';
import AuthLayout from 'shared/layouts/AuthLayout/AuthLayout';
import { Button, Input, Alert } from 'shared/components';
import StripePaymentModal from './StripePaymentModal';
import styles from './AuthView.module.css';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY || 'pk_test_dummy');

const PLANS = [
  { id: 'basico', name: 'Gratuito', price: 0 },
  { id: 'profesional', name: 'Profesional', price: 29 },
  { id: 'premium', name: 'Premium', price: 99 },
];

const FEATURES = [
  { icon: <Sparkles size={18} />, title: 'Inteligencia Artificial', description: 'Predice tus ventas y optimiza tu inventario automáticamente.' },
  { icon: <ShieldCheck size={18} />, title: 'Seguridad Total', description: 'Tus datos protegidos con encriptación de grado bancario.' },
  { icon: <Globe size={18} />, title: 'Subdominio Propio', description: 'URL personalizada y profesional para tu negocio al instante.' },
];

export default function CrearTiendaView() {
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const initialPlan = query.get('plan') || 'basico';

  const [form, setForm] = useState({
    nombre_tienda: '', schema_name: '', dominio: '',
    first_name: '', last_name: '', email: '', password: '', icono: null, plan: initialPlan
  });
  const [preview,      setPreview]      = useState(null);
  const [status,       setStatus]       = useState('idle');
  const [responseData, setResponseData] = useState(null);
  const [error,        setError]        = useState(null);

  // Stripe Modal State
  const [showStripe, setShowStripe] = useState(false);
  const [clientSecret, setClientSecret] = useState('');

  useEffect(() => {
    if (!form.nombre_tienda) return;
    const slug = form.nombre_tienda.toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, 'x').replace(/[^a-z0-9]/g, '');

    const baseDomain = process.env.REACT_APP_DOMAIN_MAIN || 'localhost';
    const suffix     = process.env.REACT_APP_TENANT_DOMAIN_SUFFIX;
    const dominio    = suffix
      ? `${slug}${suffix}`
      : baseDomain !== 'localhost'
        ? `${slug}.${baseDomain}.nip.io`
        : `${slug}.localhost`;

    setForm((prev) => ({ ...prev, schema_name: slug, dominio }));
  }, [form.nombre_tienda]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setForm(prev => ({ ...prev, icono: file }));
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('loading');
    setError(null);
    try {
      const backendPort = process.env.REACT_APP_DJANGO_PORT || '8001';
      const apiBase = `${window.location.protocol}//${window.location.hostname}:${backendPort}`;

      const formData = new FormData();
      Object.keys(form).forEach(key => {
        if (form[key]) formData.append(key, form[key]);
      });

      // Si es gratuito, creamos directo
      if (form.plan === 'basico') {
        const res  = await fetch(`${apiBase}/api/tiendas/crear/`, {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        if (!res.ok) throw data;
        setResponseData(data);
        setStatus('success');
      } else {
        // Si es pago, inicializamos el PaymentIntent
        const res = await fetch(`${apiBase}/api/tiendas/checkout-suscripcion/`, {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        if (!res.ok) throw data;
        
        setClientSecret(data.clientSecret);
        setShowStripe(true);
        setStatus('idle');
      }
    } catch (err) {
      setError(err);
      setStatus('error');
    }
  };

  const handlePaymentSuccess = async (paymentIntent) => {
    setShowStripe(false);
    setStatus('loading');
    try {
      const backendPort = process.env.REACT_APP_DJANGO_PORT || '8001';
      const apiBase = `${window.location.protocol}//${window.location.hostname}:${backendPort}`;
      
      const formData = new FormData();
      Object.keys(form).forEach(key => {
        if (form[key]) formData.append(key, form[key]);
      });
      formData.append('payment_intent', paymentIntent.id);

      const res = await fetch(`${apiBase}/api/tiendas/crear-con-pago/`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw data;
      setResponseData(data);
      setStatus('success');
    } catch (err) {
      setError("El pago fue exitoso pero hubo un error al crear la tienda. Contacta a soporte.");
      setStatus('error');
    }
  };

  if (status === 'success') {
    return (
      <AuthLayout features={FEATURES}>
        <div className={styles.successBox}>
          <div className={styles.successIcon}>
            <CheckCircle2 size={36} />
          </div>
          <div>
            <h2 style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--font-extra)', color: 'var(--color-text)', marginBottom: '8px' }}>
              ¡Tu tienda está lista!
            </h2>
            <p style={{ marginBottom: '16px' }}>Todo configurado. Empieza a vender hoy.</p>
          </div>
          <div className={styles.urlBox}>
            <p>Tu dominio exclusivo:</p>
            <strong>{responseData.dominio}</strong>
          </div>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)' }}>
            Inicia sesión con <strong>{responseData.admin_email}</strong>
          </p>
          <Button as="a" href="/login" rightIcon={<ArrowRight size={16} />} fullWidth>
            Continuar
          </Button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout features={FEATURES}>
      <div className={styles.formWrap}>
        <div className={styles.formHeader}>
          <h1 className={styles.formTitle}>Crea tu Negocio</h1>
          <p className={styles.formSubtitle}>Únete a cientos de emprendedores con MiQhatu.</p>
        </div>

        {error && (
          <Alert variant="danger" title="Error al crear tienda">
            {typeof error === 'string' ? error : JSON.stringify(error)}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.sectionTitle}><Store size={16} /> Datos de la Tienda</div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 'bold', marginBottom: '8px' }}>
              <CreditCard size={14} style={{ display: 'inline', marginRight: '4px' }} /> 
              Plan de Suscripción
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              {PLANS.map(p => (
                <div 
                  key={p.id}
                  onClick={() => setForm({...form, plan: p.id})}
                  style={{
                    flex: 1, padding: '12px', border: `2px solid ${form.plan === p.id ? 'var(--color-primary)' : 'var(--color-border)'}`,
                    borderRadius: '8px', cursor: 'pointer', textAlign: 'center', background: form.plan === p.id ? 'var(--color-primary-ghost)' : 'transparent'
                  }}
                >
                  <div style={{ fontWeight: 'bold', fontSize: '14px', color: form.plan === p.id ? 'var(--color-primary)' : 'var(--color-text)' }}>{p.name}</div>
                  <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>${p.price}/mes</div>
                </div>
              ))}
            </div>
          </div>

          <Input
            id="ct-nombre"
            label={<><Building size={14} /> Nombre de la Tienda</>}
            name="nombre_tienda"
            value={form.nombre_tienda}
            onChange={handleChange}
            placeholder="Ej: Mi Boutique Online"
            required
          />

          <div className={styles.twoCol}>
            <Input id="ct-slug" label={<><Zap size={14} /> Slug</>} name="schema_name" value={form.schema_name} disabled />
            <Input id="ct-dominio" label={<><Globe size={14} /> Dominio</>} name="dominio" value={form.dominio} disabled />
          </div>

          {/* Logo / Icono Upload */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 'bold', marginBottom: '8px' }}>
              <ImageIcon size={14} /> Icono de la Tienda (Opcional)
            </label>
            {!preview ? (
              <div style={{
                border: '2px dashed #cbd5e1', borderRadius: '12px', padding: '20px',
                textAlign: 'center', cursor: 'pointer', backgroundColor: '#f8fafc'
              }}>
                <label style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <ImageIcon size={32} color="#94a3b8" />
                  <span style={{ marginTop: '8px', color: '#64748b', fontSize: '14px' }}>Haz clic para subir un logo</span>
                  <input type="file" accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} />
                </label>
              </div>
            ) : (
              <div style={{ position: 'relative', display: 'inline-block', border: '1px solid #e2e8f0', borderRadius: '12px', overflow: 'hidden' }}>
                <img src={preview} alt="Preview" style={{ width: '100px', height: '100px', objectFit: 'cover' }} />
                <button
                  type="button"
                  onClick={() => { setForm(p => ({ ...p, icono: null })); setPreview(null); }}
                  style={{ position: 'absolute', top: '4px', right: '4px', background: 'rgba(0,0,0,0.5)', color: '#fff', border: 'none', borderRadius: '50%', padding: '4px', cursor: 'pointer' }}
                >
                  <X size={14} />
                </button>
              </div>
            )}
          </div>

          <div className={styles.sectionTitle}><User size={16} /> Datos del Dueño</div>

          <div className={styles.twoCol}>
            <Input id="ct-firstname" label="Nombre" name="first_name" value={form.first_name} onChange={handleChange} placeholder="Tu nombre" required />
            <Input id="ct-lastname"  label="Apellido" name="last_name" value={form.last_name} onChange={handleChange} placeholder="Tu apellido" required />
          </div>

          <Input id="ct-email" label={<><Mail size={14} /> Correo Electrónico</>} type="email" name="email" value={form.email} onChange={handleChange} placeholder="ejemplo@correo.com" required />
          <Input id="ct-pass"  label={<><Lock size={14} /> Contraseña</>} type="password" name="password" value={form.password} onChange={handleChange} placeholder="Mínimo 6 caracteres" required minLength={6} />

          <Button type="submit" fullWidth loading={status === 'loading'} style={{ marginTop: '8px' }}>
            Crear Mi Tienda Ahora
          </Button>
        </form>

        <p className={styles.footer}>
          ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
        </p>
      </div>

      {showStripe && clientSecret && (
        <Elements stripe={stripePromise} options={{ clientSecret, appearance: { theme: 'stripe' } }}>
          <StripePaymentModal
            clientSecret={clientSecret}
            amount={PLANS.find(p => p.id === form.plan)?.price}
            planName={PLANS.find(p => p.id === form.plan)?.name}
            onClose={() => setShowStripe(false)}
            onSuccess={handlePaymentSuccess}
          />
        </Elements>
      )}
    </AuthLayout>
  );
}
