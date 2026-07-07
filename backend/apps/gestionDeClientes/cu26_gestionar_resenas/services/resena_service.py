from django.db.models import Avg, Count

from apps.core.services import BaseService
from apps.gestionDeClientes.cu26_gestionar_resenas.models.resena import Resena
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido

# Estados que consideramos "compra verificada" para poder reseñar.
ESTADOS_COMPRA_VALIDA = ['PAGADO', 'ENTREGADO']


class ResenaService(BaseService):
    """Servicio de Reseñas y Calificaciones (CU-27)."""

    def __init__(self):
        super().__init__(Resena)

    def cliente_compro_producto(self, cliente_id, producto_id):
        """
        True si el cliente tiene un pedido PAGADO o ENTREGADO que contiene el
        producto (comprador verificado).
        """
        return Pedido.objects.filter(
            carrito__cliente_id=cliente_id,
            estado__in=ESTADOS_COMPRA_VALIDA,
            carrito__items__producto_id=producto_id,
        ).exists()

    def crear_o_actualizar(self, cliente_id, producto_id, calificacion, comentario=''):
        """
        Crea o actualiza la reseña de un cliente sobre un producto.
        Valida la calificación (1-5) y que sea un comprador verificado.
        Devuelve (instancia, creado).
        """
        try:
            calificacion = int(calificacion)
        except (TypeError, ValueError):
            raise ValueError('La calificación debe ser un número entre 1 y 5.')
        if calificacion < 1 or calificacion > 5:
            raise ValueError('La calificación debe estar entre 1 y 5 estrellas.')

        if not self.cliente_compro_producto(cliente_id, producto_id):
            raise ValueError('Solo puedes reseñar productos que compraste (pedido pagado o entregado).')

        return Resena.objects.update_or_create(
            cliente_id=cliente_id,
            producto_id=producto_id,
            defaults={'calificacion': calificacion, 'comentario': (comentario or '').strip()},
        )

    def resenas_de_producto(self, producto_id):
        """Lista las reseñas de un producto, con el cliente precargado."""
        return (
            Resena.objects
            .filter(producto_id=producto_id)
            .select_related('cliente')
            .order_by('-created_at')
        )

    def resumen_producto(self, producto_id):
        """Promedio de calificación y total de reseñas de un producto."""
        agg = Resena.objects.filter(producto_id=producto_id).aggregate(
            promedio=Avg('calificacion'),
            total=Count('id'),
        )
        return {
            'promedio': round(agg['promedio'], 2) if agg['promedio'] is not None else 0,
            'total': agg['total'] or 0,
        }

    def mi_resena(self, cliente_id, producto_id):
        """Reseña existente del cliente sobre el producto (o None)."""
        return Resena.objects.filter(cliente_id=cliente_id, producto_id=producto_id).first()
