from rest_framework import serializers
from .rol import Rol
from .tenant import Client, Domain
from ..services.tenant_service import TenantService # ✅ Importación del servicio
import re

class TenantCreateSerializer(serializers.Serializer):
    # Datos de la tienda
    nombre_tienda = serializers.CharField(max_length=100)
    schema_name   = serializers.SlugField(max_length=50)
    dominio       = serializers.CharField(max_length=100, required=False)

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

    class Meta:
        model = Client
        fields = [
            'id', 
            'nombre_comercial', 
            'descripcion', 
            'categoria_tienda', 
            'logo_url', 
            'subdominio',
            'schema_name'
        ]
        read_only_fields = fields

    def get_subdominio(self, obj):
        """
        Obtiene el subdominio (dominio principal) asociado a este tenant.
        """
        dominio = obj.domains.first()
        return dominio.domain if dominio else None