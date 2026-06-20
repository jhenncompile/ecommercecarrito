from django_tenants.test.cases import TenantTestCase
from apps.customers.clientes.models.cliente import Cliente
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito import Carrito
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.factura import Factura
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.detalle_factura import DetalleFactura
from apps.gestionDeClientes.cu17_analizar_comportamiento_del_cliente.services.behavior_service import CustomerBehaviorService

class AprioriBehaviorTestCase(TenantTestCase):
    def setUp(self):
        # 1. Llamar a super().setUp() para inicializar el test tenant y cambiar de schema
        super().setUp()

        # 2. Crear cliente para las compras
        self.cliente = Cliente.objects.create(
            nombre='Cliente Apriori',
            correo='cliente_apriori@example.com',
            contrasena='pbkdf2_sha256$260000$testpass$test',
            telefono='77777777'
        )

        # 3. Crear categoría
        self.categoria = Categoria.objects.create(nombre="Alimentos")

        # 4. Crear productos
        self.prod_a = Producto.objects.create(nombre="Leche", precio=10.0, stock=100, categoria=self.categoria)
        self.prod_b = Producto.objects.create(nombre="Cereal", precio=25.0, stock=100, categoria=self.categoria)
        self.prod_c = Producto.objects.create(nombre="Pan", precio=5.0, stock=100, categoria=self.categoria)
        self.prod_d = Producto.objects.create(nombre="Jamon", precio=15.0, stock=100, categoria=self.categoria)

    def _crear_factura(self, nro, productos):
        # Crear carrito cerrado
        carrito = Carrito.objects.create(cliente=self.cliente, estado='CERRADO')
        # Crear pedido pagado
        pedido = Pedido.objects.create(carrito=carrito, estado='PAGADO')
        # Crear factura vigente
        factura = Factura.objects.create(
            nro=nro,
            pedido=pedido,
            cliente=self.cliente,
            monto_total=sum(p.precio for p in productos),
            estado='VIGENTE'
        )
        # Crear detalles de factura
        for p in productos:
            DetalleFactura.objects.create(
                factura=factura,
                producto=p,
                cantidad=1,
                precio_unitario=p.precio,
                total=p.precio
            )
        return factura

    def test_calcular_apriori_reglas_asociacion(self):
        """
        Prueba que el algoritmo Apriori identifique correctamente las asociaciones de productos.
        Patrón de compras:
        - Factura 1: Leche, Cereal
        - Factura 2: Leche, Cereal
        - Factura 3: Leche, Cereal, Jamon
        - Factura 4: Pan, Jamon
        Esto significa que Leche y Cereal se compran juntos en 3 de 4 transacciones (75% de soporte).
        Y la confianza de Leche -> Cereal y Cereal -> Leche es 100%.
        """
        # Crear transacciones
        self._crear_factura("F001", [self.prod_a, self.prod_b])
        self._crear_factura("F002", [self.prod_a, self.prod_b])
        self._crear_factura("F003", [self.prod_a, self.prod_b, self.prod_d])
        self._crear_factura("F004", [self.prod_c, self.prod_d])

        # Calcular Apriori
        reglas = CustomerBehaviorService._calcular_apriori(min_support=0.2, min_confidence=0.5)

        # Deberían generarse reglas de asociación válidas
        self.assertTrue(len(reglas) > 0)

        # Buscar regla Leche -> Cereal
        regla_leche_cereal = next((r for r in reglas if r['antecedente'] == "Leche" and r['consecuente'] == "Cereal"), None)
        self.assertIsNotNone(regla_leche_cereal)
        self.assertEqual(regla_leche_cereal['soporte'], 75.0)
        self.assertEqual(regla_leche_cereal['confianza'], 100.0)

        # Buscar regla Cereal -> Leche
        regla_cereal_leche = next((r for r in reglas if r['antecedente'] == "Cereal" and r['consecuente'] == "Leche"), None)
        self.assertIsNotNone(regla_cereal_leche)
        self.assertEqual(regla_cereal_leche['soporte'], 75.0)
        self.assertEqual(regla_cereal_leche['confianza'], 100.0)
