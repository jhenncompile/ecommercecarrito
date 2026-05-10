def get_auth_extra_data(user):
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
        'is_superuser': user.is_superuser
    }

    if user.tenant:
        extra_data['tenant_id']   = user.tenant.id
        extra_data['schema_name'] = user.tenant.schema_name

        from django.conf import settings
        suffix = getattr(settings, 'TENANT_DOMAIN_SUFFIX', '.localhost')
        schema = user.tenant.schema_name

        # Usa siempre el sufijo del .env — NO el dominio guardado en BD
        # porque puede estar desactualizado (ej: gerle.localhost en vez de gerle.IP.nip.io)
        extra_data['subdomain'] = f"{schema}{suffix}"

    return extra_data