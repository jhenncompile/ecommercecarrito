import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, User as UserIcon, Store } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import PerfilHeader from '../components/PerfilHeader';
import PerfilForm from '../components/PerfilForm';
import TiendaPerfilForm from '../components/TiendaPerfilForm';
import TiendaSuscripcionForm from '../components/TiendaSuscripcionForm';
import { usePerfil } from '../hooks/usePerfil';
import { useTiendaPerfil } from '../hooks/useTiendaPerfil';
import './PerfilView.css';

export default function PerfilView() {
  const role = localStorage.getItem('user_role');
  const isCliente = role === 'cliente';
  
  const { perfil, loading, error, actualizar } = usePerfil();
  // Solo cargar tienda si es vendedor
  const { tiendaPerfil, loadingTienda, errorTienda, actualizarTienda } = useTiendaPerfil();
  
  const [mensaje, setMensaje] = useState(null);
  const [activeTab, setActiveTab] = useState('personal'); // 'personal', 'tienda', 'suscripcion'

  // Opcional: Leer tab de URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab && ['personal', 'tienda', 'suscripcion'].includes(tab)) {
      setActiveTab(tab);
    }
  }, []);

  const handleGuardarPerfil = async (datos) => {
    const resultado = await actualizar(datos);
    if (resultado.success) {
      setMensaje({ tipo: 'success', texto: 'Perfil actualizado correctamente' });
      setTimeout(() => setMensaje(null), 3000);
    } else {
      setMensaje({ tipo: 'error', texto: resultado.error });
    }
  };

  const handleGuardarTienda = async (datos) => {
    const resultado = await actualizarTienda(datos);
    if (resultado.success) {
      setMensaje({ tipo: 'success', texto: 'Datos de tienda actualizados correctamente' });
      setTimeout(() => setMensaje(null), 3000);
    } else {
      setMensaje({ tipo: 'error', texto: resultado.error });
    }
  };

  if (loading || (loadingTienda && !isCliente)) {
    return (
      <AppView title="Perfil">
        <div className="loading-container">Cargando información...</div>
      </AppView>
    );
  }

  return (
    <AppView title="Mi Perfil" subtitle={isCliente ? "Gestiona tu cuenta de cliente" : "Gestiona tu información y tu tienda"}>
      {/* Mensaje de estado */}
      {mensaje && (
        <div className={`alert alert-${mensaje.tipo} profile-alert animate-fade-in`}>
          {mensaje.tipo === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
          <span>{mensaje.texto}</span>
        </div>
      )}

      {(error || (errorTienda && !isCliente)) && (
        <div className="alert alert-error profile-alert">
          <AlertCircle size={20} />
          <span>{error || errorTienda}</span>
        </div>
      )}

      {/* Encabezado con foto */}
      {perfil && <PerfilHeader perfil={perfil} />}

      {/* Navegación por pestañas (solo vendedores) */}
      {!isCliente && (
        <div className="profile-tabs">
          <button 
            className={`tab-btn ${activeTab === 'personal' ? 'active' : ''}`}
            onClick={() => setActiveTab('personal')}
          >
            <UserIcon size={18} />
            Datos Personales
          </button>
          <button 
            className={`tab-btn ${activeTab === 'tienda' ? 'active' : ''}`}
            onClick={() => setActiveTab('tienda')}
          >
            <Store size={18} />
            Mi Tienda
          </button>
          <button 
            className={`tab-btn ${activeTab === 'suscripcion' ? 'active' : ''}`}
            onClick={() => setActiveTab('suscripcion')}
          >
            <CheckCircle size={18} />
            Suscripción
          </button>
        </div>
      )}

      {/* Formularios */}
      <div className="perfil-container card">
        {activeTab === 'personal' && perfil && (
          <PerfilForm
            perfil={perfil}
            onGuardar={handleGuardarPerfil}
            loading={loading}
          />
        )}
        
        {activeTab === 'tienda' && !isCliente && tiendaPerfil && (
          <TiendaPerfilForm
            perfil={tiendaPerfil}
            onGuardar={handleGuardarTienda}
            loading={loadingTienda}
          />
        )}

        {activeTab === 'suscripcion' && !isCliente && tiendaPerfil && (
          <TiendaSuscripcionForm
            perfil={tiendaPerfil}
            onGuardar={() => window.location.reload()}
          />
        )}
      </div>
    </AppView>
  );
}