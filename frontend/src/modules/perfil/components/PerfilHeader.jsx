import { User, Link as LinkIcon, Copy, BadgeCheck, ShieldCheck } from 'lucide-react';
import './PerfilHeader.css';

export default function PerfilHeader({ perfil }) {
  const role = localStorage.getItem('user_role');
  const isCliente = role === 'cliente';
  
  // Nombre a mostrar depende del modelo
  const displayTitle = isCliente 
    ? (perfil?.nombre || 'Cliente')
    : (`${perfil?.first_name || ''} ${perfil?.last_name || ''}`.trim() || 'Vendedor');

  const displayEmail = isCliente ? perfil?.correo : perfil?.email;

  const handleCopiarURL = () => {
    if (perfil?.tenant_info?.url) {
      navigator.clipboard.writeText(perfil.tenant_info.url);
      alert('URL copiada al portapapeles');
    }
  };

  return (
    <div className="perfil-header">
      <div className="perfil-foto-container">
        {perfil?.foto_perfil ? (
          <img src={perfil.foto_perfil} alt="Perfil" className="perfil-foto" />
        ) : (
          <div className={`perfil-foto-placeholder ${isCliente ? 'cliente-bg' : ''}`}>
            {isCliente ? <User size={48} /> : <ShieldCheck size={48} />}
          </div>
        )}
      </div>

      <div className="perfil-info">
        <div className="perfil-main-info">
          <h1>{displayTitle}</h1>
          <div className="perfil-badges">
            <span className={`rol-badge ${role}`}>
              {isCliente ? <User size={12} /> : <BadgeCheck size={12} />}
              {role.toUpperCase()}
            </span>
          </div>
        </div>
        
        <p className="email">{displayEmail}</p>

        {/* Información adicional del cliente */}
        {isCliente && (perfil?.telefono || perfil?.nit) && (
          <div className="perfil-extra-data">
            {perfil.telefono && <span>📞 {perfil.telefono}</span>}
            {perfil.nit && <span>📄 NIT: {perfil.nit}</span>}
          </div>
        )}

        {/* Información del tenant (solo vendedores con tienda) */}
        {!isCliente && perfil?.tenant_info && (
          <div className="tenant-info">
            <h3>Información de tu Tienda</h3>
            <div className="tenant-details">
              <div className="tenant-item">
                <span className="label">Nombre:</span>
                <span className="value">{perfil.tenant_info.nombre_tienda}</span>
              </div>
              <div className="tenant-item">
                <span className="label">Dominio:</span>
                <span className="value">{perfil.tenant_info.dominio}</span>
              </div>
              {perfil.tenant_info.url && (
                <div className="tenant-item url-item">
                  <span className="label">
                    <LinkIcon size={16} />
                    Acceso Público
                  </span>
                  <div className="url-container">
                    <a 
                      href={perfil.tenant_info.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="tenant-link"
                    >
                      {perfil.tenant_info.url}
                    </a>
                    <button 
                      className="copy-btn"
                      onClick={handleCopiarURL}
                      title="Copiar URL"
                    >
                      <Copy size={16} />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}