import React from 'react';
import { Lock, Gem, ArrowUpCircle } from 'lucide-react';
import { useTiendaPerfil } from '../../modules/perfil/hooks/useTiendaPerfil';
import Button from './Button/Button';

/**
 * RequirePremium Component
 * 
 * Envuelve cualquier vista o componente. Si la tienda no tiene acceso a la característica 
 * premium (o su límite es 0/insuficiente), renderiza un candado overlay.
 * 
 * @param {boolean} locked - Forzar el bloqueo (ej. si se alcanzó el límite de productos).
 * @param {string} title - Título del banner de bloqueo.
 * @param {string} message - Descripción de por qué está bloqueado.
 * @param {ReactNode} children - El componente protegido.
 */
export default function RequirePremium({ locked = false, title = "Función Premium", message = "Mejora tu plan para acceder a esta característica.", children }) {
  // Opcionalmente podemos auto-verificar el plan desde aquí, pero aceptar `locked` es más flexible
  // para verificar límites dinámicos (ej: productos > max_productos).
  
  if (!locked) {
    return <>{children}</>;
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Contenido Difuminado */}
      <div style={{ filter: 'blur(8px)', opacity: 0.5, pointerEvents: 'none', userSelect: 'none' }}>
        {children}
      </div>

      {/* Overlay del Candado */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '32px',
          borderRadius: '16px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          textAlign: 'center',
          maxWidth: '400px',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{ 
            background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
            width: '64px', height: '64px', borderRadius: '50%', display: 'flex',
            alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
            color: 'white', boxShadow: '0 4px 6px -1px rgba(245, 158, 11, 0.3)'
          }}>
            <Gem size={32} />
          </div>
          
          <h3 style={{ fontSize: '20px', fontWeight: '800', color: '#0f172a', marginBottom: '8px' }}>
            {title}
          </h3>
          
          <p style={{ color: '#64748b', fontSize: '14px', marginBottom: '24px', lineHeight: '1.5' }}>
            {message}
          </p>

          <Button 
            fullWidth 
            onClick={() => window.location.href = '/perfil?tab=suscripcion'}
          >
            <ArrowUpCircle size={18} style={{ marginRight: '8px' }} />
            Mejorar Plan Ahora
          </Button>
        </div>
      </div>
    </div>
  );
}
