// ============================================================
// LEGO REGISTRY — core/router/routes.config.jsx
// ============================================================
// Para añadir UN NUEVO MÓDULO a toda la app:
//
//   1. Crea tu vista en:
//      modules/mi_modulo/views/MiModuloView.jsx
//
//   2. Agrega su entrada abajo en APP_MODULES:
//      {
//        id: 'mi_modulo',
//        path: '/mi-modulo',
//        label: 'Mi Módulo',
//        icon: IconoDeLucide,
//        component: lazy(() => import('modules/mi_modulo/views/MiModuloView')),
//        protected: true,
//        inSidebar: true,
//        group: 'negocio',  // 'principal' | 'negocio' | 'analisis' | 'config'
//      }
//
//   ¡Listo! El sidebar, las rutas y el menú se actualizan solos.
// ============================================================

import { lazy } from 'react';
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Users,
  BarChart3,
} from 'lucide-react';

// ─── MÓDULOS AUTENTICADOS (con sidebar) ─────────────────────
export const APP_MODULES = [
  {
    id: 'panel',
    path: '/dashboard',
    label: 'Panel',
    icon: LayoutDashboard,
    component: lazy(() => import('modules/panel/views/PanelView')),
    protected: true,
    inSidebar: true,
    group: 'principal',
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
  },
];

// ─── RUTAS PÚBLICAS (sin autenticación) ─────────────────────
export const AUTH_ROUTES = [
  {
    id: 'home',
    path: '/',
    component: lazy(() => import('modules/auth/views/HomeView')),
  },
  {
    id: 'login',
    path: '/login',
    component: lazy(() => import('modules/auth/views/LoginView')),
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
    id: 'catalogo-vista',
    path: '/productos/catalogo',  // misma ruta que usa el navigate en CatalogoView
    component: lazy(() => import('modules/productos_catalogo/views/CatalogoView')),
    protected: true,
    inSidebar: false,  // no aparece en el sidebar
  }
  


];

// ─── Helper: agrupar módulos del sidebar por grupo ──────────
export const getSidebarGroups = () => {
  const sidebarItems = APP_MODULES.filter((m) => m.inSidebar);
  const groups = {};
  sidebarItems.forEach((item) => {
    const g = item.group || 'general';
    if (!groups[g]) groups[g] = [];
    groups[g].push(item);
  });
  return groups;
};
