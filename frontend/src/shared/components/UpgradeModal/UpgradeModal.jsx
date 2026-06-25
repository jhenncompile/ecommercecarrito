import React from 'react';
import Modal from '../Modal/Modal';
import Button from '../Button/Button';
import { Gem, ArrowUpCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function UpgradeModal({ isOpen, onClose, message }) {
  const navigate = useNavigate();

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Límite del Plan Alcanzado" zIndex={9999}>
      <div style={{ textAlign: 'center', padding: 'var(--space-4) 0' }}>
        <div style={{
          background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
          width: '64px', height: '64px', borderRadius: '50%', display: 'flex',
          alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
          color: 'white', boxShadow: '0 4px 6px -1px rgba(245, 158, 11, 0.3)'
        }}>
          <Gem size={32} />
        </div>
        
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-md)', marginBottom: 'var(--space-6)', lineHeight: '1.5' }}>
          {message || 'Has alcanzado el límite de tu plan actual. Mejora tu suscripción para seguir creciendo tu negocio.'}
        </p>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <Button variant="ghost" onClick={onClose}>
            Más tarde
          </Button>
          <Button 
            onClick={() => {
              onClose();
              navigate('/perfil?tab=suscripcion');
            }}
          >
            <ArrowUpCircle size={18} style={{ marginRight: '8px' }} />
            Mejorar Plan Ahora
          </Button>
        </div>
      </div>
    </Modal>
  );
}
