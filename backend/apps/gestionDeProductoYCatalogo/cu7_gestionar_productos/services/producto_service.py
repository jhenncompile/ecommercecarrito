from decimal import Decimal, ROUND_HALF_UP
from apps.core.services import BaseService
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto


class ProductoService(BaseService):
    def __init__(self):
        super().__init__(Producto)

    @staticmethod
    def calcular_precio(producto):
        """
        Calcula el precio final de un producto de forma centralizada para
        evitar cálculos duplicados en el frontend y las apps móviles.

        - Reutiliza el sistema de ofertas existente (Promoción vigente).
        - Si el producto está en preventa, aplica preorder_discount_percentage.
        - Los productos normales conservan su precio (o el de su promoción).

        Devuelve: {precio_original, precio_final, en_preventa}
        """
        precio_original = producto.precio or Decimal('0')
        precio_final = Decimal(precio_original)

        # 1. Sistema de ofertas existente (Promoción vigente)
        promo = getattr(producto, 'promocion', None)
        if promo and promo.vigente and promo.descuento_pct:
            precio_final *= (Decimal('1') - Decimal(promo.descuento_pct) / Decimal('100'))

        # 2. Descuento de preventa
        en_preventa = bool(getattr(producto, 'is_preorder', False))
        descuento_preventa = getattr(producto, 'preorder_discount_percentage', 0) or 0
        if en_preventa and Decimal(descuento_preventa) > 0:
            precio_final *= (Decimal('1') - Decimal(descuento_preventa) / Decimal('100'))

        precio_final = precio_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if precio_final < 0:
            precio_final = Decimal('0.00')

        return {
            'precio_original': Decimal(precio_original).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'precio_final': precio_final,
            'en_preventa': en_preventa,
        }
