import { useState } from 'react';
import { useStripe, useElements, PaymentElement } from '@stripe/react-stripe-js';
import { Button, Alert } from 'shared/components';
import { X, Lock } from 'lucide-react';
import styles from './AuthView.module.css';

export default function StripePaymentModal({ clientSecret, amount, planName, onClose, onSuccess }) {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) return;

    setIsLoading(true);
    setError(null);

    const { error: submitError, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/crear-tienda?payment_success=true`,
      },
      redirect: 'if_required',
    });

    if (submitError) {
      setError(submitError.message || "Ocurrió un error al procesar el pago.");
      setIsLoading(false);
    } else if (paymentIntent && paymentIntent.status === 'succeeded') {
      onSuccess(paymentIntent);
    } else {
      setError("Estado de pago inesperado. Por favor, revisa tu cuenta.");
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999
    }}>
      <div style={{
        background: '#fff', borderRadius: '16px', padding: '24px', width: '100%', maxWidth: '500px',
        maxHeight: '90vh', overflowY: 'auto', position: 'relative', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)'
      }}>
        <button 
          onClick={onClose}
          style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', cursor: 'pointer', color: '#64748b' }}
        >
          <X size={24} />
        </button>

        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '800', color: '#0f172a' }}>Completar Suscripción</h2>
          <p style={{ color: '#64748b', fontSize: '14px', marginTop: '4px' }}>
            Plan <strong>{planName}</strong> — ${amount}/mes
          </p>
        </div>

        {error && (
          <div style={{ marginBottom: '16px' }}>
            <Alert variant="danger" title="Error de pago">{error}</Alert>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ padding: '16px', border: '1px solid #e2e8f0', borderRadius: '8px', marginBottom: '24px' }}>
            <PaymentElement />
          </div>

          <Button type="submit" fullWidth loading={isLoading || !stripe || !elements}>
            <Lock size={16} style={{ marginRight: '8px' }} />
            Pagar Seguramente
          </Button>
          
          <p style={{ textAlign: 'center', color: '#94a3b8', fontSize: '12px', marginTop: '16px' }}>
            Pagos procesados de forma segura a través de Stripe.
          </p>
        </form>
      </div>
    </div>
  );
}
