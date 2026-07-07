import logging
import re
import django.http.request as _django_http_request

logger = logging.getLogger(__name__)

# ── Permitir guion bajo en el host ────────────────────────────────────────────
# Django (RFC 3986) rechaza hosts con "_" en request.get_host() lanzando
# DisallowedHost (HTTP 400). Sin embargo, varios schemas/subdominios de tenants
# usan guion bajo (ej. "shop_daniel39.10.49.76.200.nip.io"), lo que hacía fallar
# cualquier request a esos inquilinos (p. ej. marcar un pedido como ENTREGADO).
# Ampliamos la regex de validación de host para aceptar "_" y así django-tenants
# puede resolver esos dominios en lugar de responder 400.
_django_http_request.host_validation_re = re.compile(
    r"^([a-z0-9._-]+|\[[a-f0-9]*:[a-f0-9.:]+\])(?::([0-9]+))?$"
)


class TenantHostMiddleware:
    """
    Middleware para limpiar el host de puertos y espacios antes de que 
    django-tenants intente identificar al inquilino (tenant).
    
    Adicionalmente, mapea dinámicamente subdominios locales (ej. shoppaola94.localhost)
    al dominio real registrado en la base de datos (ej. shoppaola94.192.168.0.50.nip.io)
    para que django-tenants reconozca el inquilino sin requerir múltiples registros.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        original_host = request.get_host()
        parts = original_host.split(':')
        host = parts[0].lower().strip()
        port_suffix = f":{parts[1].strip()}" if len(parts) > 1 else ""

        request.original_host = original_host

        # Mapeo dinámico para subdominios .localhost en entorno de pruebas
        parts_host = host.split('.')
        if len(parts_host) > 1 and parts_host[-1] == 'localhost':
            subdomain = parts_host[0]
            try:
                from apps.customers.models import Domain
                matched_domain = Domain.objects.filter(
                    domain__startswith=f"{subdomain}."
                ).exclude(
                    tenant__schema_name='public'
                ).first()
                if matched_domain:
                    host = matched_domain.domain
            except Exception as e:
                logger.error(f"Error mapping localhost subdomain in TenantHostMiddleware: {str(e)}")

        try:
            logger.warning(f"TenantHostMiddleware - original_host={request.original_host} | computed_host={host} | HTTP_HOST_before={request.META.get('HTTP_HOST')}")
        except Exception:
            pass

        request.META['HTTP_HOST'] = f"{host}{port_suffix}"

        return self.get_response(request)

