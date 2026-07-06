import unicodedata
from django.db.models import Count
from apps.core.services import BaseService
from ..models.plan import Plan


def _normalizar_nombre(nombre):
    """Normaliza el nombre del plan: sin acentos, minúsculas y sin espacios extremos.
    Así 'Profesional' y 'profesional' (o 'Básico'/'basico') se tratan como el mismo tier."""
    base = unicodedata.normalize('NFKD', nombre or '')
    base = ''.join(c for c in base if not unicodedata.combining(c))
    return base.strip().lower()


class PlanService(BaseService):
    """Servicio de Planes de Suscripción."""

    def __init__(self):
        super().__init__(Plan)

    def obtener_activos(self):
        """Obtiene solo los planes activos."""
        return Plan.objects.filter(activo=True)

    def obtener_por_nombre(self, nombre):
        """Obtiene un plan por nombre."""
        return Plan.objects.filter(nombre=nombre).first()

    def obtener_planes_canonicos(self):
        """
        Devuelve el catálogo de planes sin duplicados por nombre.

        La BD puede tener el mismo tier repetido por diferencias de
        mayúsculas/acentos (p. ej. 'profesional' $99 y otro 'profesional' $29).
        Para que web y móvil usen SIEMPRE el mismo plan, se deja uno por nombre
        normalizado, eligiendo de forma determinista:
          1) el más usado por las tiendas (mayor cantidad de tenants),
          2) desempate por mayor precio (el tier real).
        Esto conserva el plan gratis (lo usan tiendas reales) y evita depender
        del orden en que la BD devuelva los registros.
        Ordenado por precio ascendente para mostrarlo en la UI.
        """
        planes = (
            Plan.objects.filter(activo=True)
            .annotate(num_tenants=Count('clientes'))
            .order_by('-num_tenants', '-precio_mensual', 'id')
        )
        canonicos = {}
        for plan in planes:
            clave = _normalizar_nombre(plan.nombre)
            if clave not in canonicos:
                canonicos[clave] = plan
        return sorted(canonicos.values(), key=lambda p: (p.precio_mensual, p.id))
