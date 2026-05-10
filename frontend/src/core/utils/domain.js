/**
 * Utilidades para manejo de dominios y subdominios en entornos Multi-Tenant (MiQhatu).
 */

/**
 * Obtiene el dominio raíz (IP o dominio base) de forma robusta.
 * Si estamos en tienda1.157.173.102.129.nip.io, debe devolver 157.173.102.129.nip.io
 */
export const getBaseDomain = (hostname) => {
  // 1. Prioridad absoluta a la variable de entorno
  if (process.env.REACT_APP_DOMAIN_MAIN && process.env.REACT_APP_DOMAIN_MAIN !== 'localhost') {
    return process.env.REACT_APP_DOMAIN_MAIN;
  }

  // 2. Manejo de localhost
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.endsWith('.localhost')) {
    return 'localhost';
  }

  // 3. Lógica para nip.io (muy común en desarrollo/VPS)
  if (hostname.includes('nip.io')) {
    const parts = hostname.split('.');
    // El formato estándar es [subdominio].IP.nip.io
    // La base (IP.nip.io) siempre son las últimas 6 partes si es IPv4
    if (parts.length >= 6) {
      return parts.slice(-6).join('.');
    }
    return hostname;
  }

  // 4. Fallback genérico para dominios normales (ej: tienda.miqhatu.com -> miqhatu.com)
  const parts = hostname.split('.');
  if (parts.length > 2) {
    return parts.slice(-2).join('.');
  }

  return hostname;
};

/**
 * Construye la URL base del API según el modo de ejecución.
 */
export const getApiUrl = (hostname, port = '8001') => {
  const apiPort = process.env.REACT_APP_DJANGO_PORT || port;
  const protocol = window.location.protocol;
  // IMPORTANTE: El API siempre se consulta al hostname actual para que el 
  // middleware de Django detecte el Tenant correctamente.
  return `${protocol}//${hostname}:${apiPort}/api`;
};
