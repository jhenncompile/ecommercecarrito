import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Box, LogOut, Bell, Search, Settings } from 'lucide-react';
import { getSidebarGroups } from 'core/router/routes.config';
import { useAuth } from 'core/hooks/useAuth';
import { useTenant } from 'core/hooks/useTenant';
import styles from './AppShell.module.css';

// ─── Etiquetas legibles para cada grupo ──────────────────────
const GROUP_LABELS = {
  principal: 'Principal',
  negocio:   'Negocio',
  analisis:  'Análisis',
  config:    'Configuración',
  cliente:   'Mi Espacio',
  general:   'General',
};

// ─── AppShell ─────────────────────────────────────────────────
// Layout principal: sidebar dinámico + topbar + área de contenido.
// El sidebar lee automáticamente routes.config.jsx — no hay que tocarlo
// para añadir nuevos módulos.
const AppShell = () => {
  const { user, logout } = useAuth();
  const tenant = useTenant();
  const navigate = useNavigate();

  const sidebarGroups = getSidebarGroups(user?.role);

  const fullName = user?.fullName || 'Usuario';
  const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=18aea4&color=fff&bold=true`;

  const handleProfileClick = () => {
    navigate('/perfil');
  };

  return (
    <div className={styles.shell}>
      {/* ━━━ SIDEBAR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <aside className={styles.sidebar}>
        {/* Brand */}
        <div className={styles.brand}>
          <Box size={26} className={styles.brandIcon} />
          <span className={styles.brandName}>MiQhatu</span>
        </div>

        {/* Nav groups — generado automáticamente desde routes.config */}
        {Object.entries(sidebarGroups).map(([group, items]) => (
          <div key={group} className={styles.navSection}>
            <span className={styles.sectionLabel}>
              {GROUP_LABELS[group] || group}
            </span>
            {items.map(({ id, path, label, icon: Icon }) => (
              <NavLink
                key={id}
                to={path}
                className={({ isActive }) =>
                  `${styles.navItem} ${isActive ? styles.active : ''}`
                }
              >
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>
        ))}

        {/* Footer */}
        <div className={styles.sidebarFooter}>
          <div className={styles.divider} />
          <NavLink
            to="/configuracion"
            className={({ isActive }) =>
              `${styles.navItem} ${isActive ? styles.active : ''}`
            }
          >
            <Settings size={18} />
            <span>Configuración</span>
          </NavLink>
          <button
            className={`${styles.navItem} ${styles.navLogout}`}
            onClick={logout}
          >
            <LogOut size={18} />
            <span>Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      {/* ━━━ MAIN AREA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <div className={styles.main}>
        {/* Topbar */}
        <header className={styles.topbar}>
          <div className={styles.searchBar}>
            <Search size={16} />
            <input
              id="global-search"
              type="text"
              placeholder="Buscar en MiQhatu..."
              aria-label="Búsqueda global"
            />
          </div>

          <div className={styles.topbarRight}>
            <div className={styles.tenantBadge}>
              <span className={styles.tenantLabel}>Tienda activa</span>
              <span className={styles.tenantValue}>{tenant}</span>
            </div>
            <div className={styles.iconBtn}>
              <Bell size={20} />
            </div>
            <div className={styles.userProfile} onClick={handleProfileClick}>
              <img
                src={avatarUrl}
                alt={fullName}
                className={styles.userAvatar}
              />
              <span className={styles.userName}>{fullName}</span>
            </div>
          </div>
        </header>

        {/* Content — aquí renderea la vista del módulo activo */}
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppShell;
