from django.conf import settings
from django_tenants.utils import tenant_context
from rest_framework import serializers
from ..models.tenant import Client, Domain
from apps.customers.users.models.usuario import Usuario

class TenantService:
    """
    Servicio encargado de la lÃ³gica de negocio para la creaciÃ³n
    de nuevos inquilinos (Tenants) y su configuraciÃ³n inicial.
    """
    
    @staticmethod
    def crear_tienda_completa(datos):
        """
        Orquesta la creaciÃ³n del esquema, el dominio y el usuario admin.
        """
        # 1. Obtener el sufijo de configuraciÃ³n (.localhost, .nip.io, etc.)
        suffix = getattr(settings, 'TENANT_DOMAIN_SUFFIX', '.localhost')
        dominio_final = f"{datos['schema_name']}{suffix}"

        # 2. Crear el objeto Client (Tenant)
        tenant = Client.objects.create(
            schema_name=datos['schema_name'],
            name=datos['nombre_tienda'],
            icono=datos.get('icono', None),
            nombre_comercial=datos['nombre_tienda'],
            plan=datos.get('plan'),
            fecha_inicio_suscripcion=datos.get('fecha_inicio_suscripcion'),
            fecha_fin_suscripcion=datos.get('fecha_fin_suscripcion')
        )

        # 3. Crear el dominio primario
        Domain.objects.create(
            domain=dominio_final,
            tenant=tenant,
            is_primary=True
        )

        # 4. Crear el usuario administrador dentro del contexto del nuevo tenant
        with tenant_context(tenant):
            # VerificaciÃ³n de seguridad en el nuevo esquema
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

            # Asignar automáticamente el rol de Administrador al dueño
            from apps.customers.users.models.rol import Rol
            
            # Crear roles básicos si no existen en este tenant
            roles_basicos = [
                {'nombre': 'Administrador', 'nivel': 1, 'descripcion': 'Dueño o administrador general'},
                {'nombre': 'Vendedor', 'nivel': 2, 'descripcion': 'Personal de ventas o empleados'},
                {'nombre': 'Cliente', 'nivel': 3, 'descripcion': 'Comprador recurrente'}
            ]
            for rb in roles_basicos:
                Rol.objects.get_or_create(
                    nombre__iexact=rb['nombre'],
                    tenant=tenant,
                    defaults={'nombre': rb['nombre'], 'nivel': rb['nivel'], 'descripcion': rb['descripcion']}
                )

            rol_admin = Rol.objects.filter(nombre__iexact='administrador', tenant=tenant).first()
            if rol_admin:
                admin.roles.add(rol_admin)

        return {
            'tienda': tenant.name,
            'schema': tenant.schema_name,
            'dominio': dominio_final,
            'admin_email': admin.email,
        }
