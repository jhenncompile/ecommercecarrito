import os
import django
import random
from django.utils.crypto import get_random_string

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from app_negocio.models import Categoria, Producto
from customers.models import Client

def obtener_instancia_categoria(nombre_cat):
    """Garantiza que devolvemos un objeto Categoria real."""
    obj, _ = Categoria.objects.get_or_create(
        nombre=nombre_cat,
        defaults={'descripcion': f'Categoría de {nombre_cat}', 'activo': True}
    )
    return obj

def poblar_productos_inteligentes(cantidad, cat_electronica, cat_hogar, cat_ropa):
    """Crea productos con descripciones para que la IA pueda comparar."""
    datos_maestros = [
        ("Laptop Gamer Pro", "Computadora de alto rendimiento con tarjeta RTX, 16GB RAM y procesador i9. Ideal para gaming y diseño."),
        ("Mouse Inalámbrico", "Mouse ergonómico con conexión bluetooth de alta velocidad y sensor óptico preciso."),
        ("Teclado Mecánico", "Teclado con switches mecánicos, luces RGB y respuesta rápida para oficina o juegos."),
        ("Audífonos Noise Cancelling", "Audífonos de diadema con cancelación activa de ruido y sonido envolvente."),
        ("Monitor 4K 27''", "Pantalla de alta resolución para profesionales del diseño y video."),
        ("Camiseta Deportiva", "Prenda de poliéster transpirable para entrenamiento intenso."),
        ("Sudadera con Capucha", "Abrigo de algodón cómodo para clima frío y estilo casual."),
        ("Cafetera Express", "Máquina de café con molino integrado para hogar u oficina."),
        ("Lámpara LED Intelligente", "Iluminación ajustable con control desde el móvil y bajo consumo.")
    ]

    for i in range(cantidad):
        # Elegir un producto del pool o uno genérico
        info = random.choice(datos_maestros) if i < len(datos_maestros) else (f"Producto {i}", "Descripción de prueba.")
        
        # Asignar categoría según el nombre
        if any(keyword in info[0] for keyword in ["Laptop", "Mouse", "Teclado", "Audífonos", "Monitor"]):
            categoria_obj = cat_electronica
        elif "Cafetera" in info[0] or "Lámpara" in info[0]:
            categoria_obj = cat_hogar
        else:
            categoria_obj = cat_ropa

        Producto.objects.create(
            nombre=info[0] if i < len(datos_maestros) else f"{info[0]} {i}",
            descripcion=info[1],
            sku=f"SKU-{get_random_string(5).upper()}",
            precio=random.uniform(20.0, 1000.0),
            stock=random.randint(5, 50),
            categoria=categoria_obj,  # <--- OBJETO REAL, NO STRING
            activo=True
        )

def ejecutar():
    tenants = Client.objects.exclude(schema_name='public')
    if not tenants.exists():
        print("❌ No hay tiendas creadas. Crea primero los tenants.")
        return

    for t in tenants:
        print(f"🚀 Poblando tienda: {t.name}...")
        with schema_context(t.schema_name):
            # Crear/obtener categorías DENTRO del contexto del tenant
            cat_electronica = obtener_instancia_categoria("Electrónica")
            cat_hogar = obtener_instancia_categoria("Hogar")
            cat_ropa = obtener_instancia_categoria("Ropa")

            Producto.objects.all().delete() # Limpiamos para no duplicar
            poblar_productos_inteligentes(15, cat_electronica, cat_hogar, cat_ropa)
            print(f"✅ 15 productos creados en {t.schema_name}")

if __name__ == "__main__":
    ejecutar()