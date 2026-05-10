from django.conf import settings
from django_tenants.utils import tenant_context
from rest_framework import serializers
from ..models.tenant import Client, Domain
from ..models.usuario import Usuario

class TenantService:
    """
    Servicio encargado de la lógica de negocio para la creación
    de nuevos inquilinos (Tenants) y su configuración inicial.
    """
    
    @staticmethod
    def crear_tienda_completa(datos):
        """
        Orquesta la creación del esquema, el dominio y el usuario admin.
        """
        # 1. Obtener el sufijo de configuración (.localhost, .nip.io, etc.)
        suffix = getattr(settings, 'TENANT_DOMAIN_SUFFIX', '.localhost')
        dominio_final = f"{datos['schema_name']}{suffix}"

        # 2. Crear el objeto Client (Tenant)
        tenant = Client.objects.create(
            schema_name=datos['schema_name'],
            name=datos['nombre_tienda'],
        )

        # 3. Crear el dominio primario
        Domain.objects.create(
            domain=dominio_final,
            tenant=tenant,
            is_primary=True
        )

        # 4. Crear el usuario administrador dentro del contexto del nuevo tenant
        with tenant_context(tenant):
            # Verificación de seguridad en el nuevo esquema
            if Usuario.objects.filter(email=datos['email']).exists():
                raise serializers.ValidationError({"email": "Ese email ya existe en esta tienda."})

            admin = Usuario.objects.create_user(
                email=datos['email'],
                password=datos['password'],
                first_name=datos['first_name'],
                last_name=datos['last_name'],
                is_staff=True,
                is_active=True,
                tenant=tenant,
            )

        return {
            'tienda': tenant.name,
            'schema': tenant.schema_name,
            'dominio': dominio_final,
            'admin_email': admin.email,
        }