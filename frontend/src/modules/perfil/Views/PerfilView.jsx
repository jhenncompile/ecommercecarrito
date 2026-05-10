import { useState } from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';
import AppView from 'shared/widgets/AppView/AppView';
import PerfilHeader from '../components/PerfilHeader';
import PerfilForm from '../components/PerfilForm';
import TiendaPerfilForm from '../components/TiendaPerfilForm';
import { usePerfil } from '../hooks/usePerfil';
import { useTiendaPerfil } from '../hooks/useTiendaPerfil';
import './PerfilView.css';

export default function PerfilView() {
  const { perfil, loading, error, actualizar } = usePerfil();
  const { tiendaPerfil, loadingTienda, errorTienda, actualizarTienda } = useTiendaPerfil();
  const [mensaje, setMensaje] = useState(null);

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

  if (loading || loadingTienda) return <AppView title="Perfil"><div>Cargando...</div></AppView>;

  return (
    <AppView title="Mi Perfil" subtitle="Gestiona tu información personal">
      {/* Mensaje de estado */}
      {mensaje && (
        <div className={`alert alert-${mensaje.tipo}`}>
          {mensaje.tipo === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
          <span>{mensaje.texto}</span>
        </div>
      )}

      {(error || errorTienda) && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          <span>{error || errorTienda}</span>
        </div>
      )}

      {/* Encabezado con foto */}
      {perfil && <PerfilHeader perfil={perfil} />}

      {/* Formulario de edición */}
      <div className="perfil-container">
        {perfil && (
          <PerfilForm
            perfil={perfil}
            onGuardar={handleGuardarPerfil}
            loading={loading}
          />
        )}
        
        {tiendaPerfil && (
          <div style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid #e2e8f0' }}>
            <TiendaPerfilForm
              perfil={tiendaPerfil}
              onGuardar={handleGuardarTienda}
              loading={loadingTienda}
            />
          </div>
        )}
      </div>
    </AppView>
  );
}