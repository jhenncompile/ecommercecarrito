import hashlib
import json
import math
from datetime import date, datetime, timedelta
from decimal import Decimal

import numpy as np
from django.db import DatabaseError
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek, TruncYear
from django.utils import timezone

from apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias.models.categoria import Categoria
from apps.gestionDeProductoYCatalogo.cu7_gestionar_productos.models.producto import Producto
from apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras.models.carrito_item import CarritoItem
from apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido.models.pedido import Pedido
from apps.gestionDeClientes.cu22_gestionar_prediccion_de_ventas.models.prediccion_cache import PrediccionCache


class ForecastService:
    ESTADOS_VENTA_CONFIRMADA = ['PAGADO', 'PROCESADO', 'ENVIADO', 'ENTREGADO']
    GRANULARIDADES = {'dia', 'semana', 'mes', 'anio'}
    TIPOS = {'ventas_cantidad', 'ventas_totales', 'por_producto', 'por_categoria'}
    DISCLAIMER_MONTO = (
        'Monto referencial calculado con precios actuales. '
        'Si los precios cambian, el monto estimado también cambiará.'
    )

    @classmethod
    def validar_configuracion(cls, config):
        errores = []
        tipo = config.get('tipo', 'ventas_cantidad')
        granularidad = cls._normalizar_granularidad(config.get('granularidad', 'mes'))

        if tipo not in cls.TIPOS:
            errores.append(f"Tipo inválido. Válidos: {', '.join(sorted(cls.TIPOS))}")

        if granularidad not in cls.GRANULARIDADES:
            errores.append(f"Granularidad inválida. Válidas: {', '.join(sorted(cls.GRANULARIDADES))}")

        data_historica_meses = cls._to_int(config.get('data_historica_meses', 12), 12)
        prediccion_meses = cls._to_int(config.get('prediccion_meses', 3), 3)

        if data_historica_meses < 3:
            errores.append('Mínimo 3 meses de datos históricos')
        if data_historica_meses > 1200:
            errores.append('Máximo 1200 meses de datos históricos')
        if prediccion_meses < 1:
            errores.append('Mínimo 1 mes de estimación')
        if prediccion_meses > 120:
            errores.append('Máximo 120 meses de estimación')

        if tipo == 'por_producto' and not config.get('producto_id'):
            errores.append('producto_id es requerido para predicción por producto')
        if tipo == 'por_categoria' and not config.get('categoria_id'):
            errores.append('categoria_id es requerido para predicción por categoría')

        return errores

    @classmethod
    def generar_prediccion(cls, config, usuario=None, usar_cache=True):
        normalized = cls._normalizar_config(config)
        cache_key = cls.cache_key(normalized)

        if usar_cache:
            cached = cls._obtener_cache(cache_key)
            if cached:
                return cached

        historico = cls._obtener_historico(normalized)
        min_periodos = 2 if normalized['granularidad'] == 'anio' else 3
        if len(historico) < min_periodos:
            raise ValueError(
                f"Se necesitan al menos {min_periodos} períodos históricos. Disponibles: {len(historico)}"
            )

        pasos = cls._calcular_pasos_prediccion(
            normalized['prediccion_meses'],
            normalized['granularidad'],
        )
        estimaciones, modelo, rmse = cls._estimar(historico, pasos)
        predicciones = cls._formatear_predicciones(normalized, historico, estimaciones)

        historico_total = sum(p['cantidad'] for p in historico)
        promedio = historico_total / len(historico) if historico else 0
        resultado = {
            'tipo': normalized['tipo'],
            'granularidad': normalized['granularidad'],
            'data_historica_meses': normalized['data_historica_meses'],
            'prediccion_meses': normalized['prediccion_meses'],
            'unidad_principal': normalized['unidad_principal'],
            'historico': historico,
            'predicciones': predicciones,
            'metricas': {
                'modelo': modelo,
                'datos_usados': len(historico),
                'cantidad_historica_total': round(historico_total, 2),
                'promedio_por_periodo': round(promedio, 2),
                'rmse_aproximado': round(rmse, 4),
                'estados_incluidos': cls.ESTADOS_VENTA_CONFIRMADA,
            },
            'confianza': 0.95,
            'disclaimer': cls.DISCLAIMER_MONTO,
            'cache_key': cache_key,
        }

        if usar_cache:
            cls._guardar_cache(cache_key, normalized, resultado, usuario)
        return resultado

    @classmethod
    def listar_productos(cls):
        return list(
            Producto.objects.filter(activo=True)
            .order_by('nombre')
            .values('id', 'nombre', 'sku', 'precio')
        )

    @classmethod
    def listar_categorias(cls):
        return list(
            Categoria.objects.filter(activo=True)
            .order_by('nombre')
            .values('id', 'nombre')
        )

    @staticmethod
    def cache_key(config):
        payload = json.dumps(config, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    @classmethod
    def _normalizar_config(cls, config):
        tipo = config.get('tipo', 'ventas_cantidad')
        if tipo == 'ventas_totales':
            tipo = 'ventas_cantidad'

        data_historica_meses = cls._to_int(config.get('data_historica_meses', 12), 12)
        prediccion_meses = cls._to_int(config.get('prediccion_meses', 3), 3)
        granularidad = cls._normalizar_granularidad(config.get('granularidad', 'mes'))

        unidad = 'ventas'
        if tipo in ('por_producto', 'por_categoria'):
            unidad = 'unidades'

        return {
            'tipo': tipo,
            'granularidad': granularidad,
            'data_historica_meses': data_historica_meses,
            'prediccion_meses': prediccion_meses,
            'producto_id': cls._to_int(config.get('producto_id'), None),
            'categoria_id': cls._to_int(config.get('categoria_id'), None),
            'unidad_principal': unidad,
        }

    @classmethod
    def _obtener_historico(cls, config):
        fecha_inicio = timezone.now() - timedelta(days=config['data_historica_meses'] * 30)
        trunc = cls._trunc_func(config['granularidad'])

        if config['tipo'] == 'ventas_cantidad':
            rows = (
                Pedido.objects.filter(
                    estado__in=cls.ESTADOS_VENTA_CONFIRMADA,
                    fecha_creacion__gte=fecha_inicio,
                )
                .annotate(periodo=trunc('fecha_creacion'))
                .values('periodo')
                .annotate(cantidad=Count('id', distinct=True))
                .order_by('periodo')
            )
        else:
            items = CarritoItem.objects.filter(
                carrito__pedido__estado__in=cls.ESTADOS_VENTA_CONFIRMADA,
                carrito__pedido__fecha_creacion__gte=fecha_inicio,
            )
            if config['tipo'] == 'por_producto':
                items = items.filter(producto_id=config['producto_id'])
            else:
                items = items.filter(producto__categoria_id=config['categoria_id'])

            rows = (
                items.annotate(periodo=trunc('carrito__pedido__fecha_creacion'))
                .values('periodo')
                .annotate(cantidad=Sum('cantidad'))
                .order_by('periodo')
            )

        puntos = [
            {
                'periodo_raw': cls._as_date(row['periodo']),
                'cantidad': float(row['cantidad'] or 0),
            }
            for row in rows
            if row['periodo'] is not None
        ]
        return cls._rellenar_periodos(puntos, config['granularidad'])

    @classmethod
    def _estimar(cls, historico, pasos):
        valores = [p['cantidad'] for p in historico]

        try:
            from statsmodels.tsa.arima.model import ARIMA

            serie = np.array(valores, dtype=float)
            modelo = ARIMA(serie, order=(1, 1, 1)).fit()
            forecast = modelo.get_forecast(steps=pasos)
            medias = forecast.predicted_mean
            conf = forecast.conf_int(alpha=0.05)
            estimaciones = []
            for idx, valor in enumerate(medias):
                if hasattr(conf, 'iloc'):
                    inferior = conf.iloc[idx, 0]
                    superior = conf.iloc[idx, 1]
                else:
                    inferior = conf[idx][0]
                    superior = conf[idx][1]
                estimaciones.append(cls._estimacion_dict(valor, inferior, superior))
            rmse = float(math.sqrt(np.mean(np.square(modelo.resid)))) if len(modelo.resid) else 0
            return estimaciones, 'ARIMA(1,1,1)', rmse
        except Exception:
            return cls._estimar_tendencia_lineal(valores, pasos)

    @classmethod
    def _estimar_tendencia_lineal(cls, valores, pasos):
        x = np.arange(len(valores), dtype=float)
        y = np.array(valores, dtype=float)

        if len(valores) >= 2:
            pendiente, intercepto = np.polyfit(x, y, 1)
            ajustados = intercepto + pendiente * x
            residuos = y - ajustados
            rmse = float(math.sqrt(np.mean(np.square(residuos)))) if len(residuos) else 0
        else:
            pendiente = 0
            intercepto = y[-1] if len(y) else 0
            rmse = 0

        estimaciones = []
        for paso in range(1, pasos + 1):
            valor = max(0, intercepto + pendiente * (len(valores) + paso - 1))
            margen = 1.96 * (rmse or max(1, valor * 0.12))
            estimaciones.append(cls._estimacion_dict(valor, valor - margen, valor + margen))

        return estimaciones, 'TENDENCIA_LINEAL', rmse

    @classmethod
    def _formatear_predicciones(cls, config, historico, estimaciones):
        precio_actual = cls._precio_referencial(config)
        cursor = cls._periodo_siguiente(cls._parse_periodo(historico[-1]['periodo']), config['granularidad'])
        predicciones = []

        for estimacion in estimaciones:
            cantidad = max(0, estimacion['cantidad_estimada'])
            monto = None
            if precio_actual is not None:
                monto = round(cantidad * float(precio_actual), 2)

            predicciones.append({
                'periodo': cls._format_periodo(cursor, config['granularidad']),
                'cantidad_estimada': round(cantidad, 2),
                'cantidad_estimada_redondeada': int(round(cantidad)),
                'precio_actual': cls._decimal_to_float(precio_actual),
                'monto_estimado_referencial': monto,
                'ic_inferior': round(max(0, estimacion['ic_inferior']), 2),
                'ic_superior': round(max(0, estimacion['ic_superior']), 2),
                'confianza': 0.95,
                'nota': cls.DISCLAIMER_MONTO if monto is not None else '',
            })
            cursor = cls._periodo_siguiente(cursor, config['granularidad'])

        return predicciones

    @classmethod
    def _precio_referencial(cls, config):
        if config['tipo'] == 'por_producto':
            producto = Producto.objects.filter(id=config['producto_id'], activo=True).first()
            return producto.precio if producto else None

        if config['tipo'] == 'por_categoria':
            return (
                Producto.objects.filter(categoria_id=config['categoria_id'], activo=True)
                .aggregate(promedio=Avg('precio'))
                .get('promedio')
            )

        return None

    @staticmethod
    def _guardar_cache(hash_config, configuracion, resultado, usuario):
        try:
            expira = timezone.now() + timedelta(hours=24)
            PrediccionCache.objects.update_or_create(
                hash_config=hash_config,
                defaults={
                    'usuario_id': getattr(usuario, 'id', None),
                    'usuario_email': getattr(usuario, 'email', '') or '',
                    'configuracion': configuracion,
                    'resultado': resultado,
                    'fecha_expiracion': expira,
                    'vigente': True,
                },
            )
        except DatabaseError:
            return None

    @staticmethod
    def _obtener_cache(hash_config):
        try:
            cache = PrediccionCache.objects.filter(
                hash_config=hash_config,
                vigente=True,
                fecha_expiracion__gt=timezone.now(),
            ).first()
            return cache.resultado if cache else None
        except DatabaseError:
            return None

    @staticmethod
    def _trunc_func(granularidad):
        return {
            'dia': TruncDate,
            'semana': TruncWeek,
            'mes': TruncMonth,
            'anio': TruncYear,
        }[granularidad]

    @classmethod
    def _rellenar_periodos(cls, puntos, granularidad):
        if not puntos:
            raise ValueError('No hay ventas confirmadas suficientes para estimar')

        valores = {cls._period_start(p['periodo_raw'], granularidad): p['cantidad'] for p in puntos}
        actual = min(valores)
        fin = cls._period_start(max(valores), granularidad)
        historico = []

        while actual <= fin:
            historico.append({
                'periodo': cls._format_periodo(actual, granularidad),
                'cantidad': round(float(valores.get(actual, 0)), 2),
            })
            actual = cls._periodo_siguiente(actual, granularidad)

        return historico

    @staticmethod
    def _calcular_pasos_prediccion(meses, granularidad):
        if granularidad == 'dia':
            return meses * 30
        if granularidad == 'semana':
            return meses * 4
        if granularidad == 'anio':
            return max(1, math.ceil(meses / 12))
        return meses

    @staticmethod
    def _periodo_siguiente(periodo, granularidad):
        if granularidad == 'dia':
            return periodo + timedelta(days=1)
        if granularidad == 'semana':
            return periodo + timedelta(days=7)
        if granularidad == 'anio':
            return date(periodo.year + 1, 1, 1)

        year = periodo.year + (1 if periodo.month == 12 else 0)
        month = 1 if periodo.month == 12 else periodo.month + 1
        return date(year, month, 1)

    @staticmethod
    def _period_start(value, granularidad):
        value = ForecastService._as_date(value)
        if granularidad == 'semana':
            return value - timedelta(days=value.weekday())
        if granularidad == 'mes':
            return date(value.year, value.month, 1)
        if granularidad == 'anio':
            return date(value.year, 1, 1)
        return value

    @staticmethod
    def _format_periodo(value, granularidad):
        if granularidad == 'anio':
            return value.strftime('%Y')
        if granularidad == 'mes':
            return value.strftime('%Y-%m')
        return value.strftime('%Y-%m-%d')

    @staticmethod
    def _parse_periodo(value):
        if len(value) == 4:
            return date(int(value), 1, 1)
        if len(value) == 7:
            return datetime.strptime(value, '%Y-%m').date()
        return datetime.strptime(value, '%Y-%m-%d').date()

    @staticmethod
    def _normalizar_granularidad(value):
        aliases = {
            'ano': 'anio',
            'año': 'anio',
            'year': 'anio',
        }
        value = str(value or 'mes').lower()
        return aliases.get(value, value)

    @staticmethod
    def _as_date(value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return value.date()

    @staticmethod
    def _estimacion_dict(valor, inferior, superior):
        return {
            'cantidad_estimada': float(max(0, valor)),
            'ic_inferior': float(max(0, inferior)),
            'ic_superior': float(max(0, superior)),
        }

    @staticmethod
    def _to_int(value, default):
        if value in (None, ''):
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _decimal_to_float(value):
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        return float(value)
