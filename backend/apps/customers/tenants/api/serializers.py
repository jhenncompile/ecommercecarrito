from rest_framework import serializers
from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.models.rol import Rol
from apps.customers.tenants.models.tenant import Client, Domain
from ..services.tenant_service import TenantService # âœ… ImportaciÃ³n del servicio
import re

class TenantCreateSerializer(serializers.Serializer):
    # Datos de la tienda
    nombre_tienda = serializers.CharField(max_length=100)
    schema_name   = serializers.SlugField(max_length=50)
    dominio       = serializers.CharField(max_length=100, required=False)
    icono         = serializers.ImageField(required=False, allow_null=True)

    # Datos del dueÃ±o
    email         = serializers.EmailField()
    password      = serializers.CharField(write_only=True, min_length=6)
    first_name    = serializers.CharField(max_length=50)
    last_name     = serializers.CharField(max_length=50)

    def validate_schema_name(self, value):
        if Client.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError("Ya existe una tienda con ese schema.")
        if not re.match(r'^[a-z][a-z0-9_]+$', value):
            raise serializers.ValidationError("Solo letras minÃºsculas, nÃºmeros y guiÃ³n bajo.")
        return value

    def validate_dominio(self, value):
        if value and Domain.objects.filter(domain=value).exists():
            raise serializers.ValidationError("Ese dominio ya estÃ¡ en uso.")
        return value

    def create(self, validated_data):
        """
        Delega la creaciÃ³n compleja al servicio de dominio.
        """
        return TenantService.crear_tienda_completa(validated_data)


class TiendaPublicSerializer(serializers.ModelSerializer):
    """
    Serializador pÃºblico de tiendas para el Marketplace (Escenario C).
    Solo expone informaciÃ³n comercial, sin datos sensibles del tenant.
    """
    subdominio = serializers.SerializerMethodField()
    store_url = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 
            'nombre_comercial', 
            'name',
            'descripcion', 
            'categoria_tienda', 
            'logo_url', 
            'icono',
            'subdominio',
            'schema_name',
            'store_url'
        ]
        read_only_fields = fields

    def get_subdominio(self, obj):
        """
        Obtiene el subdominio (dominio principal) asociado a este tenant.
        """
        dominio = obj.domains.first()
        return dominio.domain if dominio else None
        
    def get_store_url(self, obj):
        """
        Genera la URL completa de la tienda para el frontend web.
        Usa la cabecera 'origin' para detectar el puerto de la UI (ej: 3000).
        """
        from django.conf import settings
        import re
        
        request = self.context.get('request')
        origin = request.headers.get('origin') if request else None
from rest_framework import serializers
from apps.gestionDeUsuarioySeguridad.cu4_gestion_de_roles.models.rol import Rol
from apps.customers.tenants.models.tenant import Client, Domain
from ..services.tenant_service import TenantService # ✅ Importación del servicio
import re

class TenantCreateSerializer(serializers.Serializer):
    # Datos de la tienda
    nombre_tienda = serializers.CharField(max_length=100)
    schema_name   = serializers.SlugField(max_length=50)
    dominio       = serializers.CharField(max_length=100, required=False)
    icono         = serializers.ImageField(required=False, allow_null=True)

    # Datos del dueño
    email         = serializers.EmailField()
    password      = serializers.CharField(write_only=True, min_length=6)
    first_name    = serializers.CharField(max_length=50)
    last_name     = serializers.CharField(max_length=50)

    def validate_schema_name(self, value):
        if Client.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError("Ya existe una tienda con ese schema.")
        if not re.match(r'^[a-z][a-z0-9_]+$', value):
            raise serializers.ValidationError("Solo letras minúsculas, números y guión bajo.")
        return value

    def validate_dominio(self, value):
        if value and Domain.objects.filter(domain=value).exists():
            raise serializers.ValidationError("Ese dominio ya está en uso.")
        return value

    def create(self, validated_data):
        """
        Delega la creación compleja al servicio de dominio.
        """
        return TenantService.crear_tienda_completa(validated_data)


class TiendaPublicSerializer(serializers.ModelSerializer):
    """
    Serializador público de tiendas para el Marketplace (Escenario C).
    Solo expone información comercial, sin datos sensibles del tenant.
    """
    subdominio = serializers.SerializerMethodField()
    store_url = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 
            'nombre_comercial', 
            'descripcion', 
            'categoria_tienda', 
            'logo_url', 
            'icono',
            'subdominio',
            'schema_name',
            'store_url'
        ]
        read_only_fields = fields

    def get_subdominio(self, obj):
        """
        Obtiene el subdominio (dominio principal) asociado a este tenant.
        """
        dominio = obj.domains.first()
        return dominio.domain if dominio else None
        
    def get_store_url(self, obj):
        """
        Genera la URL completa de la tienda para el frontend web.
        Usa la cabecera 'origin' para detectar el puerto de la UI (ej: 3000).
        """
        from django.conf import settings
        import re
        
        request = self.context.get('request')
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
            
        domain_main = getattr(settings, 'DOMAIN_MAIN', 'localhost')
        is_ip = bool(re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', domain_main))
        
        subdomain_str = obj.domains.first().domain.split('.')[0] if obj.domains.first() else obj.schema_name.replace('_', '-').replace(' ', '-').lower()
        
        if domain_main in ['localhost', '127.0.0.1']:
            suffix = '.localhost'
        elif is_ip or 'nip.io' in domain_main:
            ip = domain_main if is_ip else domain_main.replace('.nip.io', '')
            suffix = f".{ip}.nip.io"
        else:
            # Producción real: miqhatu.com
            suffix = f".{domain_main}"
            
        return f"{protocol}://{subdomain_str}{suffix}{port_str}"

class TiendaPrivadaSerializer(serializers.ModelSerializer):
    """
    Serializador privado para el dueño de la tienda.
    Incluye información de suscripción, plan y métricas de uso (límites).
    """
    subdominio = serializers.SerializerMethodField()
    plan_detalle = serializers.SerializerMethodField()
    uso = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'nombre_comercial', 'descripcion', 'categoria_tienda', 
            'logo_url', 'icono', 'subdominio', 'schema_name', 
            'plan', 'plan_detalle', 'fecha_inicio_suscripcion', 'fecha_fin_suscripcion', 'uso'
        ]
        read_only_fields = fields

    def get_subdominio(self, obj):
        dominio = obj.domains.first()
        return dominio.domain if dominio else None

    def get_plan_detalle(self, obj):
        if not obj.plan:
            return None
        return {
            'id': obj.plan.id,
            'nombre': obj.plan.nombre,
            'precio_mensual': obj.plan.precio_mensual,
            'max_productos': obj.plan.max_productos,
            'max_usuarios': obj.plan.max_usuarios,
        }

    def get_uso(self, obj):
        from django.db import connection
        
        productos_actuales = 0
        usuarios_actuales = 0
        
        # Validar que estemos en el schema correcto
        if connection.schema_name == obj.schema_name:
            from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
            from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.models.usuario import Usuario
            productos_actuales = Producto.objects.count()
            usuarios_actuales = Usuario.objects.count()
            
        return {
            'productos': productos_actuales,
            'usuarios': usuarios_actuales
        }

from rest_framework import serializers
from apps.customers.tenants.models.plan import Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'nombre', 'descripcion', 'precio_mensual', 
            'precio_anual', 'max_usuarios', 'max_productos', 
            'facturacion_max', 'activo', 'permisos'
        ]
        read_only_fields = ['id']
