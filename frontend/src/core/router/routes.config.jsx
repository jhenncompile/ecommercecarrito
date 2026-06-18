// ============================================================
// LEGO REGISTRY — core/router/routes.config.jsx
// ============================================================

import { lazy } from 'react';
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Users,
  BarChart3,
  User,
  ClipboardList,
  ShoppingBag,
  Shield,
  Store,
  Database,
  TrendingUp,
  Bell,
} from 'lucide-react';

// ─── MÓDULOS AUTENTICADOS (con sidebar) ─────────────────────
export const APP_MODULES = [
  {
    id: 'admin',
    path: '/su',
    label: 'Bitácora',
    icon: Shield,
    component: lazy(() => import('modules/admin/views/AdminView')),
    protected: true,
    inSidebar: true,
    group: 'admin',
    roles: ['admin'],
  },
  {
    id: 'admin_tiendas',
    path: '/su/tiendas',
    label: 'Gestión Tiendas',
    icon: Store,
    component: lazy(() => import('modules/admin/views/AdminTiendasView')),
    protected: true,
    inSidebar: true,
    group: 'admin',
    roles: ['admin'],
  },
  {
    id: 'admin_roles',
    path: '/su/roles',
    label: 'Gestionar Roles',
    icon: Users,
    component: lazy(() => import('modules/admin/views/RolesView')),
    protected: true,
    inSidebar: true,
    group: 'admin',
    roles: ['admin'],
  },
  {
    id: 'admin_permisos',
    path: '/su/permisos',
    label: 'Gestionar Permisos',
    icon: Shield,
    component: lazy(() => import('modules/admin/views/PermisosView')),
    protected: true,
    inSidebar: true,
    group: 'admin',
    roles: ['admin'],
  },
  {
    id: 'admin_usuarios',
    path: '/su/usuarios',
    label: 'Gestionar Usuarios',
    icon: Users,
    component: lazy(() => import('modules/admin/views/UsersView')),
    protected: true,
    inSidebar: true,
    group: 'admin',
    roles: ['admin'],
  },
  {
    id: 'admin_backups',
    path: '/su/backups',
    label: 'Backups Sistema',
    icon: Database,
    component: lazy(() => import('modules/admin/views/BackupsView')),
    protected: true,
    inSidebar: true,
    group: 'admin',
    roles: ['admin'],
  },
  {
    id: 'panel',
    path: '/dashboard',
    label: 'Panel',
    icon: LayoutDashboard,
    component: lazy(() => import('modules/panel/views/PanelView')),
    protected: true,
    inSidebar: true,
    group: 'principal',
    roles: ['vendedor'],
  },
  {
    id: 'negocio_usuarios',
    path: '/usuarios',
    label: 'Usuarios / Personal',
    icon: Users,
    component: lazy(() => import('modules/admin/views/UsersView')),
    protected: true,
    inSidebar: true,
    group: 'negocio',
    roles: ['vendedor'],
    requireOwner: true,
  },
  {
    id: 'productos',
    path: '/productos',
    label: 'Productos',
    icon: Package,
    component: lazy(() => import('modules/productos_catalogo/views/ProductosView')),
    protected: true,
    inSidebar: true,
    group: 'negocio',
    roles: ['vendedor'],
  },
  {
    id: 'ventas',
    path: '/ventas',
    label: 'Ventas',
    icon: ShoppingCart,
    component: lazy(() => import('modules/ventas_facturacion/views/VentasView')),
    protected: true,
    inSidebar: true,
    group: 'negocio',
    roles: ['vendedor'],
  },
  {
    id: 'clientes',
    path: '/clientes',
    label: 'Clientes',
    icon: Users,
    component: lazy(() => import('modules/clientes/views/ClientesView')),
    protected: true,
    inSidebar: true,
    group: 'negocio',
    roles: ['vendedor'],
  },
  {
    id: 'inventario',
    path: '/inventario',
    label: 'Inventario',
    icon: ClipboardList,
    component: lazy(() => import('modules/inventario/views/InventarioView')),
    protected: true,
    inSidebar: true,
    group: 'negocio',
    roles: ['vendedor'],
  },
  {
    id: 'reportes',
    path: '/reportes',
    label: 'Reportes',
    icon: BarChart3,
    component: lazy(() => import('modules/reportes/views/ReportesView')),
    protected: true,
    inSidebar: true,
    group: 'analisis',
    roles: ['vendedor'],
  },
  {
    id: 'predicciones',
    path: '/predicciones',
    label: 'Predicciones IA',
    icon: TrendingUp,
    component: lazy(() => import('modules/reportes/views/Predicciones/PredictionView')),
    protected: true,
    inSidebar: true,
    group: 'analisis',
    roles: ['vendedor'],
  },
  {
    id: 'recordatorios',
    path: '/recordatorios',
    label: 'Recordatorios',
    icon: Bell,
    component: lazy(() => import('modules/recordatorios/views/RecordatoriosView')),
    protected: true,
    inSidebar: true,
    group: 'config',
    roles: ['vendedor'],
  },
  {
    id: 'perfil',
    path: '/perfil',
    label: 'Mi Perfil',
    icon: User,
    component: lazy(() => import('modules/perfil/Views/PerfilView')),
    protected: true,
    inSidebar: true,
    group: 'config',
    roles: ['vendedor', 'cliente'],
  },
  {
    id: 'cliente_dashboard',
    path: '/mi-portal',
    label: 'Mi Portal',
    icon: User,
    component: lazy(() => import('modules/cliente/views/ClienteDashboard')),
    protected: true,
    inSidebar: true,
    group: 'cliente',
    roles: ['cliente'],
  },
  {
    id: 'marketplace',
    path: '/marketplace',
    component: lazy(() => import('modules/marketplace/views/MarketplaceView')),
    protected: true,
    inSidebar: false,
    roles: ['vendedor', 'cliente'],
  },
  {
    id: 'mis_pedidos',
    path: '/pedidos',
    label: 'Mis Pedidos',
    icon: ShoppingBag,
    component: lazy(() => import('modules/cliente/views/MisPedidosView')),
    protected: true,
    inSidebar: true,
    group: 'cliente',
    roles: ['cliente'],
  }
];

// ─── RUTAS PÚBLICAS (sin autenticación) ─────────────────────
export const AUTH_ROUTES = [
  {
    id: 'home',
    path: '/',
    component: lazy(() => import('modules/auth/views/HomeView')),
  },
  {
    id: 'tienda-catalogo',
    path: '/catalogo',
    component: lazy(() => import('modules/tienda/views/PublicStorefront')),
  },
  {
    id: 'login',
    path: '/login',
    component: lazy(() => import('modules/auth/views/LoginView')),
  },
  {
    id: 'registro',
    path: '/registro-cliente',
    component: lazy(() => import('modules/auth/views/RegistroView')),
  },
  {
    id: 'forgot-password',
    path: '/forgot-password',
    component: lazy(() => import('modules/auth/views/ForgotPasswordView')),
  },
  {
    id: 'reset-password',
    path: '/reset-password/:uid/:token',
    component: lazy(() => import('modules/auth/views/ResetPasswordView')),
  },
  {
    id: 'crear-tienda',
    path: '/crear-tienda',
    component: lazy(() => import('modules/auth/views/CrearTiendaView')),
  },
  {
    id: 'tiendas',
    path: '/tiendas',
    component: lazy(() => import('modules/auth/views/ListaTiendasView')),
  },
  {
    id: 'sso',
    path: '/sso',
    component: lazy(() => import('modules/auth/views/SSOReceiverView')),
  },
  {
    id: 'tienda-publica',
    path: '/tienda',
    component: lazy(() => import('modules/tienda/views/PublicStorefront')),
  },
  {
    id: 'catalogo-vista',
    path: '/productos/catalogo',
    component: lazy(() => import('modules/productos_catalogo/views/CatalogoView')),
    protected: true,
    inSidebar: false,
  }
];

// ─── Helper: agrupar módulos del sidebar por grupo ──────────
export const getSidebarGroups = (user) => {
  if (!user) return {};
  const userRole = user.role;
  const isOwner = user.is_staff || user.is_superuser;

  const sidebarItems = APP_MODULES.filter(
    (m) => {
      if (!m.inSidebar) return false;
      if (!m.roles?.includes(userRole)) return false;
      if (m.requireOwner && !isOwner) return false;
      return true;
    }
  );
  const groups = {};
  sidebarItems.forEach((item) => {
    const g = item.group || 'general';
    if (!groups[g]) groups[g] = [];
    groups[g].push(item);
  });
  return groups;
};
