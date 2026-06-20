import django_filters
from rest_framework import filters
from django.db import models

class ProductoAtributosFilterBackend(filters.BaseFilterBackend):
    """
    Filtro dinamico personalizado para filtrar por atributos JSON.
    Ejemplo de uso en URL: ?attr_color=rojo&attr_talla=M
    """
    def filter_queryset(self, request, queryset, view):
        params = request.query_params
        attr_filters = {
            f"atributos__{key[5:]}__icontains": value 
            for key, value in params.items() 
            if key.startswith('attr_')
        }
        
        if attr_filters:
            queryset = queryset.filter(**attr_filters)
            
        return queryset
