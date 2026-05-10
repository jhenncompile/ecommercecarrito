/**
 * Utilidades para manejo de dominios y subdominios en entornos Multi-Tenant (MiQhatu).
 * Migrado desde src/utils/domain.js → src/core/utils/domain.js
 */

/**
 * Obtiene la IP base o el dominio raíz de forma robusta.
 */
export const getBaseDomain = (hostname) => {
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.endsWith('.localhost')) {
    return process.env.REACT_APP_DOMAIN_MAIN === 'localhost' || !process.env.REACT_APP_DOMAIN_MAIN
      ? 'localhost'
      : process.env.REACT_APP_DOMAIN_MAIN;
  }
  return process.env.REACT_APP_DOMAIN_MAIN || hostname;
};

/**
 * Construye la URL base del API según el modo de ejecución asegurando
 * que el Host header enviado coincida con el tenant en el que estamos.
 */
export const getApiUrl = (hostname, port = '8001') => {
  const apiPort = process.env.REACT_APP_DJANGO_PORT || port;
  const protocol = window.location.protocol;
  return `${protocol}//${hostname}:${apiPort}/api`;
};
