import React, { useState, useEffect } from 'react';
import { Crown, CheckCircle2, AlertTriangle, Star } from 'lucide-react';
import { Button, Alert } from 'shared/components';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import StripePaymentModal from '../../auth/views/StripePaymentModal';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY || 'pk_test_dummy');

export default function TiendaSuscripcionForm({ perfil, onGuardar }) {
  const [planes, setPlanes] = useState([]);
  const [loadingPlanes, setLoadingPlanes] = useState(true);
  const [showStripe, setShowStripe] = useState(false);
  const [clientSecret, setClientSecret] = useState('');
  const [selectedPlanId, setSelectedPlanId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlanes = async () => {
      try {
        const backendPort = process.env.REACT_APP_DJANGO_PORT || '8001';
        const apiBase = `${window.location.protocol}//${window.location.hostname}:${backendPort}`;
        const token = localStorage.getItem('access_token');
        const res = await fetch(`${apiBase}/api/planes/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        setPlanes(data.results || data);
      } catch (err) {
        console.error("Error al cargar planes", err);
      } finally {
        setLoadingPlanes(false);
      }
    };
    fetchPlanes();
  }, []);

  const planActual = perfil.plan_detalle;
  const uso = perfil.uso;

  const maxProd = planActual?.max_productos ?? 50;
  const isIlimitado = maxProd === 0;
  const prodPercent = isIlimitado ? 0 : Math.min(100, Math.round((uso.productos / maxProd) * 100));
  
  let pColor = '#10b981';
  if (prodPercent > 80) pColor = '#f59e0b';
  if (prodPercent >= 100) pColor = '#ef4444';

  const handleUpgradeClick = async (planId) => {
    setSelectedPlanId(planId);
    setLoading(true);
    setError(null);
    try {
      const backendPort = process.env.REACT_APP_DJANGO_PORT || '8001';
      const apiBase = `${window.location.protocol}//${window.location.hostname}:${backendPort}`;
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(`${apiBase}/api/tienda/suscripcion/upgrade/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ plan_id: planId })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Error al inicializar pago');
      
      if (data.clientSecret) {
        setClientSecret(data.clientSecret);
        setShowStripe(true);
      } else if (data.success) {
        onGuardar();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentSuccess = async (paymentIntent) => {
    setShowStripe(false);
    setLoading(true);
    try {
      const backendPort = process.env.REACT_APP_DJANGO_PORT || '8001';
      const apiBase = `${window.location.protocol}//${window.location.hostname}:${backendPort}`;
      const token = localStorage.getItem('access_token');

      const res = await fetch(`${apiBase}/api/tienda/suscripcion/upgrade/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          plan_id: selectedPlanId,
          payment_intent: paymentIntent.id 
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Error al validar pago');
      
      onGuardar();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loadingPlanes) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>Cargando planes de suscripción...</div>;
  }

  const currentPlanNivel = planActual ? parseFloat(planActual.precio_mensual) : -1;

  return (
    <div>
      <div style={{ marginBottom: '24px', padding: '24px', background: 'linear-gradient(to right, #f8fafc, #f1f5f9)', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <div style={{ background: '#3b82f6', color: '#fff', padding: '8px', borderRadius: '8px' }}>
            <Crown size={24} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', color: '#0f172a' }}>Plan Actual: {planActual?.nombre || 'Ninguno'}</h3>
            <p style={{ margin: 0, color: '#64748b', fontSize: '14px' }}>
              Renovación: {perfil.fecha_fin_suscripcion || 'No aplica'}
            </p>
          </div>
        </div>

        <div style={{ marginTop: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#334155' }}>Límite de Productos</span>
            <span style={{ fontSize: '14px', color: pColor, fontWeight: 'bold' }}>
              {uso.productos} / {isIlimitado ? 'Ilimitado' : maxProd}
            </span>
          </div>
          <div style={{ width: '100%', height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${prodPercent}%`, height: '100%', background: pColor, transition: 'width 0.3s ease' }} />
          </div>
          {prodPercent >= 90 && !isIlimitado && (
            <p style={{ color: '#ef4444', fontSize: '12px', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <AlertTriangle size={14} /> Estás a punto de alcanzar tu límite. Actualiza tu plan para seguir creciendo.
            </p>
          )}
        </div>
      </div>

      {error && <Alert variant="danger" title="Error" style={{ marginBottom: '16px' }}>{error}</Alert>}

      <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '16px' }}>Mejorar Suscripción</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        {planes.map(p => {
          const isCurrent = planActual?.id === p.id || planActual?.nombre?.toLowerCase() === p.nombre.toLowerCase();
          const pNivel = parseFloat(p.precio_mensual);
          const isDowngradeOrSame = currentPlanNivel >= pNivel;

          return (
            <div key={p.id} style={{
              border: `2px solid ${isCurrent ? '#3b82f6' : '#e2e8f0'}`,
              borderRadius: '12px', padding: '20px', textAlign: 'center',
              background: isCurrent ? '#eff6ff' : '#fff', position: 'relative'
            }}>
              {isCurrent && <div style={{ position: 'absolute', top: '-10px', right: '10px', background: '#3b82f6', color: 'white', padding: '2px 8px', borderRadius: '12px', fontSize: '10px', fontWeight: 'bold' }}>ACTUAL</div>}
              <h4 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#0f172a', textTransform: 'capitalize' }}>{p.nombre}</h4>
              <div style={{ fontSize: '24px', fontWeight: '900', color: '#1e293b', marginBottom: '16px' }}>${p.precio_mensual}<span style={{ fontSize: '12px', color: '#64748b', fontWeight: 'normal' }}>/mes</span></div>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 24px 0', textAlign: 'left', fontSize: '13px', color: '#475569' }}>
                <li style={{ marginBottom: '8px' }}><CheckCircle2 size={14} style={{ color: '#10b981', marginRight: '4px', verticalAlign: 'middle' }}/> {p.max_productos === 0 ? 'Productos Ilimitados' : `Hasta ${p.max_productos} Productos`}</li>
                <li style={{ marginBottom: '8px' }}><CheckCircle2 size={14} style={{ color: '#10b981', marginRight: '4px', verticalAlign: 'middle' }}/> {p.max_usuarios === 0 ? 'Usuarios Ilimitados' : `Hasta ${p.max_usuarios} Usuarios`}</li>
                {p.permisos && p.permisos.length > 0 && (
                  <li style={{ marginBottom: '8px' }}>
                    <Star size={14} style={{ color: '#f59e0b', marginRight: '4px', verticalAlign: 'middle' }}/> 
                    {p.permisos.length} Módulos Premium
                  </li>
                )}
                {p.descripcion && (
                  <li style={{ marginBottom: '8px', color: '#64748b', fontStyle: 'italic' }}>
                    {p.descripcion}
                  </li>
                )}
              </ul>
              <Button 
                fullWidth 
                variant={isCurrent ? 'secondary' : (isDowngradeOrSame ? 'outline' : 'primary')}
                disabled={isDowngradeOrSame || loading}
                onClick={() => handleUpgradeClick(p.id)}
              >
                {isCurrent ? 'Plan Actual' : (isDowngradeOrSame ? 'No Disponible' : 'Seleccionar')}
              </Button>
            </div>
          );
        })}
      </div>

      {showStripe && clientSecret && (
        <Elements stripe={stripePromise} options={{ clientSecret, appearance: { theme: 'stripe' } }}>
          <StripePaymentModal
            clientSecret={clientSecret}
            amount={planes.find(p => p.id === selectedPlanId)?.precio_mensual}
            planName={planes.find(p => p.id === selectedPlanId)?.nombre}
            onClose={() => setShowStripe(false)}
            onSuccess={handlePaymentSuccess}
          />
        </Elements>
      )}
    </div>
  );
}
