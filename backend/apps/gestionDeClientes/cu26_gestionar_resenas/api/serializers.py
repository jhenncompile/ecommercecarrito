from rest_framework import serializers

from apps.gestionDeClientes.cu26_gestionar_resenas.models.resena import Resena


class ResenaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)

    class Meta:
        model = Resena
        fields = ['id', 'producto', 'cliente', 'cliente_nombre', 'calificacion', 'comentario', 'created_at']
        read_only_fields = ['id', 'cliente', 'cliente_nombre', 'created_at']
