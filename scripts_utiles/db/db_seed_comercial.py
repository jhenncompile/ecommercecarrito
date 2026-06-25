#!/usr/bin/env python
# ========================================================================
# SCRIPT DE SEEDERS COMERCIALES - SOLO DATOS DE NEGOCIO (SIN PERMISOS/ROLES)
# ========================================================================

import os
import sys
import random
import socket
import re
from datetime import timedelta
from pathlib import Path
from django.utils.crypto import get_random_string
from django.core.management import call_command
from django.db import connection

# Configuración de Rutas
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

try:
    from faker import Faker
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.console import Console
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "faker", "rich"])
    from faker import Faker
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.console import Console

console = Console()

from django_tenants.utils import tenant_context, schema_context, schema_exists
from django.utils import timezone
from apps.customers.models import Client, Domain, Usuario, Rol, Plan, Cliente
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito import Carrito
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito_item import CarritoItem
from apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago.models.tipo_pago import TipoPago
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.detalle_factura import DetalleFactura
from apps.gestionDeVentasYFacturacion.cu14_generar_facturacion.models.factura import Factura

fake = Faker(['es_ES', 'es_MX'])

class BusinessGenerator:
    PASSWORD_STANDAR = "Pass123@"
    ESTADOS_PEDIDO_VENTA = ['PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO']
    PERIODOS_PEDIDOS_DIAS = {
        '1a': 365,
        '1m': 30,
        '1s': 7,
    }
    
    KEYWORDS_POR_CATEGORIA = {
        'Electrónica': ['pro', 'procesador', 'digital', 'inteligente', 'batería', 'conexión', 'velocidad', 'tech', 'pantalla', 'inalámbrico', 'bluetooth', 'wifi', 'sensor', 'circuito', 'voltaje', 'corriente', 'usb', 'hdmi', 'led', 'audio', 'cámara', 'resolución', 'memoria', 'almacenamiento', 'carga', 'cable', 'microcontrolador', 'placa', 'amplificador', 'frecuencia', 'portátil', 'gadget'],
        'Moda': ['algodón', 'tela', 'diseño', 'estilo', 'elegante', 'confort', 'tendencia', 'ropa', 'vestido', 'camisa', 'pantalón', 'zapatos', 'talla', 'costura', 'casual', 'formal', 'urbano', 'temporada', 'invierno', 'verano', 'accesorios', 'cuero', 'denim', 'boutique', 'calzado', 'chaqueta', 'abrigo', 'textil', 'estampado', 'moda'],
        'Hogar': ['decoración', 'madera', 'interior', 'moderno', 'calidad', 'duradero', 'confort', 'casa', 'mueble', 'sofá', 'iluminación', 'cocina', 'baño', 'jardín', 'limpieza', 'organización', 'espacio', 'minimalista', 'cerámica', 'vidrio', 'electrodoméstico', 'descanso', 'cama', 'almohada', 'sala', 'comedor', 'terraza', 'climatización', 'hogar'],
        'Salud': ['vital', 'natural', 'orgánico', 'bienestar', 'cuidado', 'suplemento', 'fit', 'vitaminas', 'nutrición', 'piel', 'higiene', 'medicina', 'terapia', 'relajación', 'saludable', 'vegano', 'proteína', 'dieta', 'cuerpo', 'mente', 'clínico', 'prevención', 'antioxidante', 'colágeno', 'hidratación', 'metabolismo', 'farmacia'],
        'Deportes': ['rendimiento', 'fuerza', 'entrenamiento', 'atlético', 'deporte', 'dinámico', 'gimnasio', 'fitness', 'cardio', 'resistencia', 'flexibilidad', 'muscular', 'zapatillas', 'pelota', 'bicicleta', 'natación', 'correr', 'yoga', 'pesas', 'competición', 'outdoor', 'rutina', 'suplementación', 'ciclismo', 'maratón', 'cancha', 'equipo'],
        'Informática y Redes': ['servidor', 'router', 'switch', 'nube', 'software', 'hardware', 'código', 'datos', 'red', 'hosting', 'vps', 'programación', 'sistema', 'computadora', 'laptop', 'teclado', 'ratón', 'monitor', 'almacenamiento', 'ssd', 'lan', 'proxy', 'base de datos', 'linux'],
        'Videojuegos': ['consola', 'pc', 'gamer', 'multijugador', 'aventura', 'acción', 'rpg', 'gráficos', 'mando', 'headset', 'streaming', 'fps', 'indie', 'logros', 'virtual', 'arcade', 'narrativo', 'simulador', 'online', 'launcher', 'mod'],
        'Herramientas y Bricolaje': ['taladro', 'destornillador', 'soldador', 'medición', 'tester', 'crimpadora', 'pinzas', 'taller', 'reparación', 'mantenimiento', 'voltímetro', 'tornillo', 'tuerca', 'llave', 'martillo', 'sierra', 'bricolaje', 'industrial', 'precisión'],
        'Automotriz': ['motor', 'aceite', 'neumático', 'freno', 'batería', 'suspensión', 'vehículo', 'coche', 'filtro', 'bujía', 'escape', 'carrocería', 'llanta', 'volante', 'parabrisas', 'refrigerante', 'embrague', 'tuning', 'gps', 'accesorios', 'moto', 'repuesto', 'lubricante', 'mecanica'],
        'Belleza y Cuidado Personal': ['maquillaje', 'crema', 'champú', 'loción', 'perfume', 'facial', 'cabello', 'uñas', 'cosmético', 'sérum', 'labial', 'máscara', 'afeitado', 'spa', 'exfoliante', 'antiedad', 'limpieza', 'fragancia', 'cuidado', 'peine', 'dermatológico', 'hidratante', 'barba'],
        'Mascotas': ['perro', 'gato', 'alimento', 'pienso', 'juguete', 'correa', 'collar', 'cama', 'acuario', 'jaula', 'rascador', 'veterinario', 'antiparasitario', 'pelaje', 'arena', 'premio', 'transportín', 'champú', 'arnés', 'mascota', 'ave', 'roedor', 'higiene'],
        'Alimentos y Bebidas': ['gourmet', 'vino', 'café', 'té', 'snack', 'orgánico', 'chocolate', 'dulce', 'salado', 'cerveza', 'licor', 'receta', 'ingrediente', 'panadería', 'carne', 'lácteo', 'conserva', 'bebida', 'jugo', 'vegano', 'sin gluten', 'artesanal', 'despensa', 'sabor'],
        'Juguetes y Juegos': ['infantil', 'peluche', 'bloques', 'rompecabezas', 'mesa', 'educativo', 'muñeca', 'figura', 'armable', 'aire libre', 'creativo', 'aprendizaje', 'diversión', 'niño', 'familia', 'cartas', 'magia', 'ciencia', 'habilidad', 'radiocontrol', 'didáctico', 'puzzle'],
        'Arte y Manualidades': ['pintura', 'lienzo', 'pincel', 'acuarela', 'dibujo', 'escultura', 'papel', 'tijeras', 'pegamento', 'arcilla', 'óleo', 'esbozo', 'caballete', 'paleta', 'creatividad', 'artesanía', 'tejido', 'hilo', 'costura', 'marcadores', 'boceto', 'papelería'],
        'Música e Instrumentos': ['guitarra', 'piano', 'batería', 'bajo', 'cuerda', 'viento', 'percusión', 'teclado', 'amplificador', 'micrófono', 'partitura', 'acústico', 'eléctrico', 'pedal', 'púa', 'afinador', 'sintetizador', 'sonido', 'estudio', 'mezcla', 'dj', 'vinilo'],
        'Viajes y Equipaje': ['maleta', 'mochila', 'viaje', 'pasaporte', 'vuelo', 'hotel', 'turismo', 'aventura', 'camping', 'tienda', 'saco', 'mapa', 'guía', 'equipaje', 'cabina', 'candado', 'almohada', 'adaptador', 'destino', 'ruta', 'excursión', 'outdoor'],
        'Libros y Educación': ['novela', 'ficción', 'ensayo', 'historia', 'ciencia', 'infantil', 'escolar', 'cuaderno', 'lápiz', 'bolígrafo', 'lectura', 'página', 'autor', 'editorial', 'diccionario', 'enciclopedia', 'aprendizaje', 'curso', 'academia', 'libro', 'literatura', 'texto'],
        'Fotografía y Video': ['lente', 'objetivo', 'trípode', 'flash', 'foco', 'estudio', 'edición', 'obturador', 'diafragma', 'iso', 'enfoque', 'macro', 'retrato', 'paisaje', 'drone', 'gimbal', 'estabilizador', 'filtro', 'fotógrafo', 'fotografía', 'grabación', 'luces'],
        'Jardinería y Exteriores': ['planta', 'maceta', 'semilla', 'tierra', 'abono', 'fertilizante', 'poda', 'riego', 'manguera', 'césped', 'flores', 'huerto', 'botánica', 'cultivo', 'invernadero', 'pala', 'rastrillo', 'insecticida', 'paisajismo', 'barbacoa', 'exterior'],
        'Bebés y Maternidad': ['pañal', 'biberón', 'cuna', 'cochecito', 'chupete', 'lactancia', 'maternidad', 'pediatra', 'gateo', 'sonajero', 'mordedor', 'babero', 'toallita', 'fórmula', 'infantil', 'recién nacido', 'guardería', 'andador', 'bañera', 'esterilizador', 'prematuro'],
        'Papelería y Oficina': ['escritorio', 'silla', 'impresora', 'tinta', 'toner', 'papel', 'archivador', 'carpeta', 'bolígrafo', 'marcador', 'agenda', 'calendario', 'clip', 'grapadora', 'pizarra', 'fotocopiadora', 'ergonómico', 'organizador', 'notas', 'cuaderno', 'oficina'],
        'Fiestas y Eventos': ['globo', 'guirnalda', 'tarta', 'vela', 'decoración', 'disfraz', 'invitación', 'celebración', 'cumpleaños', 'boda', 'aniversario', 'cotillón', 'piñata', 'catering', 'banquete', 'animación', 'confeti', 'photocall', 'karaoke', 'regalo', 'evento'],
        'Cine y Series': ['película', 'actor', 'actriz', 'director', 'guion', 'taquilla', 'estreno', 'cartelera', 'episodio', 'temporada', 'documental', 'animación', 'comedia', 'drama', 'terror', 'suspenso', 'butaca', 'palomitas', 'producción', 'cine', 'cortometraje'],
        'Bienes Raíces': ['inmobiliaria', 'venta', 'alquiler', 'hipoteca', 'departamento', 'terreno', 'parcela', 'propiedad', 'inversión', 'aval', 'contrato', 'comisión', 'agente', 'tasación', 'catastro', 'notaría', 'escritura', 'plusvalía', 'arrendamiento', 'condominio'],
        'Finanzas y Negocios': ['bolsa', 'acciones', 'mercado', 'capital', 'empresa', 'emprendimiento', 'startup', 'contabilidad', 'impuestos', 'ahorro', 'crédito', 'préstamo', 'interés', 'dividendo', 'presupuesto', 'factura', 'comercio', 'marketing', 'ventas', 'economía'],
        'Criptomonedas y Web3': ['blockchain', 'bitcoin', 'ethereum', 'token', 'nft', 'wallet', 'billetera', 'minería', 'staking', 'exchange', 'descentralizado', 'defi', 'metaverso', 'altcoin', 'cripto', 'hash', 'fiat', 'liquidez', 'contrato inteligente', 'criptomoneda'],
        'Agricultura y Ganadería': ['tractor', 'cosecha', 'siembra', 'ganado', 'granja', 'agrícola', 'campo', 'forraje', 'pastoreo', 'arado', 'fertilización', 'pesticida', 'agronomía', 'avicultura', 'porcino', 'bovino', 'lechería', 'corral', 'agro', 'campesino'],
        'Periféricos y Setup': ['teclado mecánico', 'switch', 'keycap', 'ratón ergonómico', 'dpi', 'polling rate', 'alfombrilla', 'monitor ultrawide', 'tasa de refresco', 'panel ips', 'oled', 'hub usb', 'webcam', 'micrófono condensador', 'brazo articulado', 'auriculares', 'dac'],
        'Desarrollo y DevOps': ['api', 'framework', 'repositorio', 'git', 'docker', 'kubernetes', 'contenedor', 'microservicios', 'backend', 'frontend', 'fullstack', 'python', 'javascript', 'rust', 'compilador', 'debugger', 'deploy', 'servidor web', 'pipeline'],
        'Inteligencia Artificial': ['machine learning', 'deep learning', 'red neuronal', 'dataset', 'algoritmo', 'modelo', 'entrenamiento', 'inferencia', 'nlp', 'visión computacional', 'chatbot', 'tensor', 'gpu computing', 'big data', 'analítica', 'prompt'],
        'Ciberseguridad': ['firewall', 'antivirus', 'malware', 'ransomware', 'encriptación', 'vpn', 'pentesting', 'vulnerabilidad', 'exploit', 'phishing', 'troyano', 'auditoría', 'biometría', 'token', 'criptografía', 'zero day'],
        'Impresión 3D y Makers': ['filamento', 'pla', 'abs', 'resina', 'extrusor', 'cama caliente', 'stl', 'gcode', 'slicer', 'boquilla', 'arduino', 'raspberry pi', 'prototipado', 'cnc', 'corte láser', 'motor paso a paso'],
        'Móviles y Wearables': ['smartphone', 'tablet', 'smartwatch', 'banda inteligente', 'ios', 'android', 'amoled', 'carga rápida', 'nfc', 'esim', 'snapdragon', 'gorilla glass', 'notch', 'stylus', 'powerbank'],
        'Redes y Conectividad': ['fibra óptica', 'latencia', 'ancho de banda', 'mesh', 'punto de acceso', 'cable ethernet', 'cat6', 'dns', 'ip', 'mac', 'tcp', 'udp', 'topología', 'firewall de hardware', 'puerto'],
        'Almacenamiento Avanzado': ['raid', 'nas', 'das', 'san', 'disco sólido', 'nvme gen4', 'heatsink', 'caché', 'iops', 'servidor de archivos', 'backup', 'recuperación de datos', 'partición', 'formato', 'nube híbrida'],
        'Domótica Avanzada': ['knx', 'z-wave', 'sonoff', 'home assistant', 'actuador', 'relé inteligente', 'termostato', 'persiana motorizada', 'cerradura biométrica', 'timbre inteligente', 'sensor de presencia', 'infrarrojo', 'gateway', 'tuya', 'escena', 'automatización'],
        'Internet de las Cosas (IoT)': ['esp32', 'esp8266', 'nodemcu', 'lora', 'lorawan', 'sigfox', 'rfid', 'nfc', 'telemetría', 'scada', 'edge computing', 'mqtt', 'servidor local', 'beacon', 'smart city', 'm2m', 'ipv6', 'broker', 'nube iot'],
        'Componentes Electrónicos Básicos': ['resistencia', 'capacitor', 'condensador', 'diodo', 'transistor', 'mosfet', 'inductancia', 'relé', 'protoboard', 'pcb', 'smd', 'circuito integrado', 'soldadura', 'estaño', 'jumper', 'potenciómetro', 'varistor'],
        'Sensores y Módulos': ['ultrasonido', 'pir', 'acelerómetro', 'giroscopio', 'magnetómetro', 'sensor de temperatura', 'dht11', 'dht22', 'ldr', 'fotorresistencia', 'caudalímetro', 'módulo bluetooth', 'módulo wifi', 'gps', 'gsm', 'sim800l', 'barómetro'],
        'Robótica y Mecatrónica': ['servomotor', 'motor paso a paso', 'puente h', 'pwm', 'chasis', 'rueda mecanum', 'brazo robótico', 'lidar', 'slam', 'control pid', 'encoder', 'engranaje', 'actuador lineal', 'cinemática', 'drone', 'controlador de vuelo'],
        'Energía y Alimentación': ['panel solar', 'batería lipo', 'bms', 'regulador de voltaje', 'step down', 'step up', 'inversor', 'celda de litio', '18650', 'cargador tp4056', 'fuente conmutada', 'transformador', 'rectificador', 'fusible', 'buck converter'],
        'Herramientas de Laboratorio': ['osciloscopio', 'multímetro', 'cautín', 'estación de soldadura', 'fuente de laboratorio', 'generador de funciones', 'analizador lógico', 'pinza amperimétrica', 'microscopio digital', 'malla desoldadora', 'flux', 'pelacables']
    }

    @staticmethod
    def obtener_ip_dominio():
        base_domain = os.environ.get('REACT_APP_DOMAIN_MAIN')
        if not base_domain or base_domain == 'localhost' or '192.168' in base_domain:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return f"{ip}.nip.io"
            except Exception: return "localhost"
        return base_domain

    @staticmethod
    def schema_tienda_seguro():
        for _ in range(100):
            raw_name = fake.unique.company()
            parts = re.split(r'[^a-zA-Z0-9]+', raw_name)
            parts = [p for p in parts if p]
            if not parts:
                clean_name = get_random_string(8, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            else:
                clean_name = parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])

            schema = f"shop{clean_name}"[:20]
            if not Client.objects.filter(schema_name=schema).exists():
                return schema

        return f"shop{get_random_string(12, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')}"

    @staticmethod
    def parse_rango_fechas(entrada):
        from datetime import datetime
        ahora = timezone.now()
        entrada = (entrada or '1m').strip().lower()
        
        if entrada in BusinessGenerator.PERIODOS_PEDIDOS_DIAS:
            dias = BusinessGenerator.PERIODOS_PEDIDOS_DIAS[entrada]
            return ahora - timedelta(days=dias), ahora

        partes = entrada.split()
        try:
            if len(partes) == 1:
                y = int(partes[0])
                return timezone.make_aware(datetime(y, 1, 1)), timezone.make_aware(datetime(y, 12, 31, 23, 59, 59))
            elif len(partes) == 2:
                y1, y2 = map(int, partes)
                return timezone.make_aware(datetime(y1, 1, 1)), timezone.make_aware(datetime(y2, 12, 31, 23, 59, 59))
            elif len(partes) == 3:
                d, m, y = map(int, partes)
                return timezone.make_aware(datetime(y, m, d)), ahora
            elif len(partes) == 6:
                d1, m1, y1, d2, m2, y2 = map(int, partes)
                return timezone.make_aware(datetime(y1, m1, d1)), timezone.make_aware(datetime(y2, m2, d2, 23, 59, 59))
        except Exception as e:
            pass
        return ahora - timedelta(days=30), ahora

    @staticmethod
    def fecha_aleatoria_rango(start, end):
        delta = end - start
        int_delta = int(delta.total_seconds())
        if int_delta <= 0: return start
        return start + timedelta(seconds=random.randint(0, int_delta))

    @staticmethod
    def random_product_data(categoria_obj):
        cat_nombre = categoria_obj.nombre
        kws = BusinessGenerator.KEYWORDS_POR_CATEGORIA.get(cat_nombre, [fake.word() for _ in range(3)])
        kw_principal = random.choice(kws).capitalize()
        kw_desc = " ".join(random.sample(kws, min(len(kws), 5)))
        adjetivos = [
            # Los que ya tenías
            "Pro", "Ultra", "Max", "Lite", "Edition", "Master",
            
            # Gamas y Niveles
            "Plus", "Premium", "Elite", "Essential", "Ultimate", "Basic", "Deluxe", 
            "Prime", "Signature", "Core", "Advanced", "Extreme", "Classic", "Supreme",
            
            # Tamaños y Formatos
            "Mini", "Micro", "Nano", "XL", "Compact", "Portable", "Slim", "Heavy Duty",
            
            # Tecnología y Casos de Uso
            "Smart", "Wireless", "AI", "Quantum", "Hybrid", "Gaming", "Studio", 
            "Enterprise", "Home", "Industrial", "Eco", "Digital", "Cloud",
            
            # Rendimiento y Versiones
            "Turbo", "Performance", "Overclocked", "Evolution", "Next-Gen", 
            "V2", "Gen 2", "X", "Pro Max", "Series S", "Series X", "FE"
        ]
        nombre = f"{kw_principal} {random.choice(adjetivos)} {get_random_string(3).upper()}"
        return {
            'nombre': nombre,
            'sku': f"SKU-{get_random_string(8).upper()}",
            'precio': round(random.uniform(50, 4500), 2),
            'stock': random.randint(0, 100),
            'categoria': categoria_obj,
            'activo': True,
            'descripcion': f"{fake.sentence()} {kw_desc}. Calidad superior para {cat_nombre}.",
            'imagen_url': f"https://picsum.photos/seed/{get_random_string(5)}/500/500"
        }

class DatabaseSeeder:
    def __init__(self):
        self.base_domain = BusinessGenerator.obtener_ip_dominio()

    def sync_tenant_schema(self, tenant):
        if not schema_exists(tenant.schema_name):
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA {connection.ops.quote_name(tenant.schema_name)}')
            connection.set_schema_to_public()
        call_command(
            'migrate_schemas',
            tenant=True,
            schema_name=tenant.schema_name,
            run_syncdb=True,
            interactive=False,
            verbosity=0,
        )

    def get_or_create_tenant(self, schema, defaults):
        tenant = Client.objects.filter(schema_name=schema).first()
        created = tenant is None
        if created:
            tenant = Client(schema_name=schema, **defaults)
            tenant.auto_create_schema = False
            tenant.save()
        else:
            for field, value in defaults.items():
                setattr(tenant, field, value)
            tenant.auto_create_schema = False
            tenant.save()

        self.sync_tenant_schema(tenant)
        return tenant, created

    def ensure_tenant_admin(self, tenant, rol_admin):
        user, created = Usuario.objects.get_or_create(
            email=f"admin@{tenant.schema_name.lower()}.com",
            defaults={'tenant': tenant, 'is_staff': True},
        )
        if created:
            user.set_password(BusinessGenerator.PASSWORD_STANDAR)
        user.tenant = tenant
        user.is_staff = True
        user.save()
        user.roles.add(rol_admin)
        return user

    def ejecutar_sincronizacion(self, n_tiendas, n_clientes, p_por_tienda, o_por_cliente, periodo_pedidos='1m'):
        console.print(f"\n[bold magenta]--- [INFO] Motor Especializado Comercial ---[/bold magenta]")
        fecha_inicio, fecha_fin = BusinessGenerator.parse_rango_fechas(periodo_pedidos)

        with schema_context('public'):
            todos_los_planes = list(Plan.objects.all())
            if not todos_los_planes:
                console.print("[bold red][!] Error: No hay planes en la base de datos.[/bold red]")
                return
            try:
                rol_admin = Rol.objects.get(nombre='Administrador', tenant=None)
            except Rol.DoesNotExist:
                console.print("[bold red][!] Error: No existe el rol Administrador global.[/bold red]")
                return

        # Animación de carga usando Rich
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None, complete_style="green", finished_style="bold green"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TextColumn("[yellow]{task.completed}/{task.total}")
        ) as progress:
            
            task_main = progress.add_task("[bold magenta]Progreso Global...", total=4)

            # Fase 1: Tiendas
            progress.update(task_main, description="[bold magenta]Fase 1/4: Generando Tiendas...")
            if n_tiendas > 0:
                task_t = progress.add_task("[cyan]  -> Creando Tiendas...", total=n_tiendas)
                for _ in range(n_tiendas):
                    nombre = fake.company()
                    with schema_context('public'):
                        schema = BusinessGenerator.schema_tienda_seguro()
                        plan_aleatorio = random.choice(todos_los_planes)
                        tenant, _ = self.get_or_create_tenant(
                            schema,
                            {
                                'name': nombre,
                                'plan': plan_aleatorio,
                                'nombre_comercial': nombre,
                                'categoria_tienda': fake.job(),
                            },
                        )
                        domain_str = f"{schema.lower()}.{self.base_domain}" if self.base_domain != 'localhost' else f"{schema.lower()}.localhost"
                        Domain.objects.get_or_create(domain=domain_str, tenant=tenant, defaults={'is_primary': True})
                        self.ensure_tenant_admin(tenant, rol_admin)
                    progress.advance(task_t)
            progress.advance(task_main)

            # Fase 2: Clientes
            progress.update(task_main, description="[bold magenta]Fase 2/4: Generando Clientes...")
            if n_clientes > 0:
                task_c = progress.add_task("[yellow]  -> Registrando Clientes...", total=n_clientes)
                with schema_context('public'):
                    for _ in range(n_clientes):
                        nombre_cliente = fake.name()
                        nombre_limpio = re.sub(r'[^a-z0-9]', '', nombre_cliente.lower().split()[0])
                        dominio_limpio = random.choice(['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 'mail.com'])
                        sufijo = random.randint(10, 9999)
                        correo_cliente = f"{nombre_limpio}{sufijo}@{dominio_limpio}"
                        c, created = Cliente.objects.get_or_create(correo=correo_cliente, defaults={'nombre': nombre_cliente})
                        if created: c.set_password(BusinessGenerator.PASSWORD_STANDAR); c.save()
                        progress.advance(task_c)
            progress.advance(task_main)

            # Fase 3: Productos
            progress.update(task_main, description="[bold magenta]Fase 3/4: Generando Productos...")
            todas = list(Client.objects.exclude(schema_name='public'))
            all_cat_names = list(BusinessGenerator.KEYWORDS_POR_CATEGORIA.keys())

            if p_por_tienda > 0 and todas:
                total_prods = len(todas) * p_por_tienda
                task_p = progress.add_task("[green]  -> Añadiendo Productos...", total=total_prods)
                
                for tenant in todas:
                    self.sync_tenant_schema(tenant)
                    self.ensure_tenant_admin(tenant, rol_admin)

                for tenant in todas:
                    with tenant_context(tenant):
                        tienda_cats = random.sample(all_cat_names, random.randint(1, 3))
                        cat_objects = [Categoria.objects.get_or_create(nombre=cn)[0] for cn in tienda_cats]
                        for _ in range(p_por_tienda):
                            try:
                                Producto.objects.create(**BusinessGenerator.random_product_data(random.choice(cat_objects)))
                            except Exception:
                                pass
                            progress.advance(task_p)
                        TipoPago.objects.get_or_create(nombre='Efectivo')
            progress.advance(task_main)

            # Fase 4: Pedidos
            progress.update(task_main, description="[bold magenta]Fase 4/4: Generando Pedidos...")
            if o_por_cliente > 0 and todas:
                todos_clientes = list(Cliente.objects.all())
                total_orders = len(todas) * len(todos_clientes) * o_por_cliente
                task_o = progress.add_task("[orange3]  -> Procesando Transacciones...", total=total_orders)
                
                from django.db import transaction

                for t_destino in todas:
                    with tenant_context(t_destino):
                        prods = list(Producto.objects.filter(activo=True))
                        if not prods:
                            progress.advance(task_o, len(todos_clientes) * o_por_cliente)
                            continue
                        
                        tipo_pago = TipoPago.objects.first()
                        
                        # Generar lista de órdenes a crear
                        orders_to_process = []
                        for cliente in todos_clientes:
                            orders_to_process.extend([cliente] * o_por_cliente)
                            
                        batch_size = 3000
                        
                        for i in range(0, len(orders_to_process), batch_size):
                            chunk = orders_to_process[i : i + batch_size]
                            
                            carritos_to_create = []
                            pedidos_data = []
                            
                            for cliente in chunk:
                                fecha_pedido = BusinessGenerator.fecha_aleatoria_rango(fecha_inicio, fecha_fin)
                                estado_pedido = random.choice(BusinessGenerator.ESTADOS_PEDIDO_VENTA)
                                
                                n_prods = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
                                prods_pedido = random.sample(prods, min(n_prods, len(prods)))
                                
                                items_info = []
                                monto_total = 0
                                for p in prods_pedido:
                                    cant = random.randint(1, 3)
                                    items_info.append((p, cant))
                                    monto_total += p.precio * cant
                                    
                                carrito = Carrito(cliente=cliente, estado='CERRADO', fecha_creacion=fecha_pedido, fecha_actualizacion=fecha_pedido)
                                carritos_to_create.append(carrito)
                                
                                pedidos_data.append({
                                    'cliente': cliente,
                                    'fecha': fecha_pedido,
                                    'estado': estado_pedido,
                                    'monto': monto_total,
                                    'items': items_info
                                })
                                
                            with transaction.atomic():
                                # 1. Bulk Create Carritos (Retorna IDs en PostgreSQL)
                                created_carritos = Carrito.objects.bulk_create(carritos_to_create)
                                
                                carrito_items_to_create = []
                                pedidos_to_create = []
                                
                                for idx, carrito in enumerate(created_carritos):
                                    pdata = pedidos_data[idx]
                                    
                                    for p, cant in pdata['items']:
                                        carrito_items_to_create.append(
                                            CarritoItem(carrito=carrito, producto=p, cantidad=cant, fecha_agregado=pdata['fecha'])
                                        )
                                        
                                    pedidos_to_create.append(
                                        Pedido(
                                            carrito=carrito, 
                                            estado=pdata['estado'], 
                                            fecha_creacion=pdata['fecha'], 
                                            fecha_actualizacion=pdata['fecha']
                                        )
                                    )
                                    
                                # 2. Bulk Create Items & Pedidos
                                CarritoItem.objects.bulk_create(carrito_items_to_create)
                                created_pedidos = Pedido.objects.bulk_create(pedidos_to_create)
                                
                                facturas_to_create = []
                                for idx, pedido in enumerate(created_pedidos):
                                    pdata = pedidos_data[idx]
                                    facturas_to_create.append(
                                        Factura(
                                            nro=f"FAC-{get_random_string(10).upper()}",
                                            pedido=pedido,
                                            cliente=pdata['cliente'],
                                            tipo_pago=tipo_pago,
                                            monto_total=pdata['monto'],
                                            estado='VIGENTE',
                                            fecha=pdata['fecha'].date(),
                                            hora=pdata['fecha'].time()
                                        )
                                    )
                                    
                                # 3. Bulk Create Facturas
                                created_facturas = Factura.objects.bulk_create(facturas_to_create)
                                
                                detalles_to_create = []
                                for idx, factura in enumerate(created_facturas):
                                    pdata = pedidos_data[idx]
                                    for p, cant in pdata['items']:
                                        detalles_to_create.append(
                                            DetalleFactura(
                                                factura=factura,
                                                producto=p,
                                                cantidad=cant,
                                                precio_unitario=p.precio,
                                                total=p.precio * cant
                                            )
                                        )
                                        
                                # 4. Bulk Create Detalles
                                DetalleFactura.objects.bulk_create(detalles_to_create)
                                
                            progress.advance(task_o, len(chunk))
                            
            progress.advance(task_main)
            progress.update(task_main, description="[bold green]¡Sincronización Finalizada con Éxito!")

def main():
    seeder = DatabaseSeeder()
    try:
        console.print("\n[bold cyan]========================================================[/bold cyan]")
        console.print("[bold yellow]  POBLADOR COMERCIAL DE DATOS (Solo Negocio)[/bold yellow]")
        console.print("[bold cyan]========================================================[/bold cyan]")
        nt = int(console.input("¿Tiendas (Tenants) nuevas a crear? [10]: ") or 10)
        nc = int(console.input("¿Clientes globales nuevos a registrar? [100]: ") or 100)
        pp = int(console.input("¿Productos A AÑADIR por cada tienda? [50]: ") or 50)
        op = int(console.input("¿Pedidos A GENERAR por cliente en CADA tienda? [5]: ") or 5)
        periodo = console.input("¿Rango de fechas para los pedidos históricos? [1a (1 año)]\n  (Formatos: '1m', '1a', '2002', '2002 2026', '18 12 2002', '18 12 2002 12 12 2026'): ") or '1a'
        seeder.ejecutar_sincronizacion(nt, nc, pp, op, periodo)
    except KeyboardInterrupt: pass
    except Exception as e: console.print(f"[bold red]Error: {e}[/bold red]"); import traceback; traceback.print_exc()

if __name__ == '__main__': main()
