def get_auth_extra_data(user, request=None):
    """
    Obtiene la informaci\u00f3n adicional necesaria tras un login exitoso.
    IMPORTANTE: El subdomain SIEMPRE se construye con TENANT_DOMAIN_SUFFIX del .env
    para garantizar redirects correctos en todos los modos (localhost, IP, Nginx).
    """
    extra_data = {
        'user_name':   user.email,
        'full_name':   user.get_full_name() or user.email.split('@')[0].capitalize(),
        'tenant_id':   None,
        'schema_name': None,
        'subdomain':   None,
        'is_superuser': user.is_superuser,
        'is_staff':    user.is_staff,
        'role':        'cliente'
    }

    # Determinar rol de forma compatible con las rutas del frontend
    if user.is_superuser:
        extra_data['role'] = 'admin'
    else:
        # Todo usuario (modelo Usuario) de una tienda usa el rol 'vendedor' en el frontend
        # independientemente de si es dueño (is_staff=True) o empleado normal (is_staff=False)
        extra_data['role'] = 'vendedor'


    if user.tenant:
        extra_data['tenant_id']   = user.tenant.id
        extra_data['schema_name'] = user.tenant.schema_name

        from django.conf import settings
        suffix = getattr(settings, 'TENANT_DOMAIN_SUFFIX', '.localhost')
        schema = user.tenant.schema_name

        # Usa siempre el sufijo del .env â€” NO el dominio guardado en BD
        # porque puede estar desactualizado (ej: gerle.localhost en vez de gerle.IP.nip.io)
        extra_data['subdomain'] = f"{schema}{suffix}"
        
        # Generar el store_url para redirecciones
        origin = request.headers.get('origin') if request else None
        if origin:
            from urllib.parse import urlparse
            parsed = urlparse(origin)
            protocol = parsed.scheme
            port_str = f":{parsed.port}" if parsed.port else ""
        else:
            protocol = "https" if request and request.is_secure() else "http"
            port = request.META.get('SERVER_PORT', '') if request else ''
            port_str = f":{port}" if port and port not in ['80', '443'] else ""
            
        extra_data['store_url'] = f"{protocol}://{schema}{suffix}{port_str}"

    return extra_data
