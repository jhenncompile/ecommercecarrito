# Datos de Implementación - BACKEND

## 📁 Estructura de Carpetas

```
backend/apps/negocio/reportes/
├── services/
│   ├── report_service.py           # (YA EXISTE)
│   └── [NUEVO] forecast_service.py # Lógica de predicción ARIMA
│
├── api/
│   ├── views.py                    # (YA EXISTE)
│   ├── serializers.py              # (YA EXISTE)
│   ├── urls.py                     # (ACTUALIZAR)
│   │
│   └── [NUEVO] forecast_views.py   # ViewSet de predicciones
│
├── models/
│   ├── reporte_config.py           # (YA EXISTE)
│   └── [NUEVO] prediccion_cache.py # Caché de predicciones
│
├── utils/
│   ├── pdf_generator.py            # (YA EXISTE)
│   └── [NUEVO] excel_generator.py  # Exportar Excel predicciones
│
└── __init__.py
```

---

## 🧠 SERVICIO: forecast_service.py

**Responsabilidad:** Lógica de predicción con ARIMA

```python
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import pandas as pd
import numpy as np
from django.db.models import Sum, Count
from apps.negocio.ordenes.models.pedido import Pedido
from apps.negocio.catalogo.models.producto import Producto
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class ForecastService:
    """Servicio de predicción de ventas con ARIMA."""
    
    # Orden ARIMA recomendada (p, d, q)
    ARIMA_ORDER = (1, 1, 1)
    MIN_DATA_REQUIRED = 3  # Meses mínimos
    
    @staticmethod
    def _validar_datos_suficientes(datos, meses_requeridos):
        """Valida que hay suficientes datos históricos."""
        if len(datos) < meses_requeridos:
            raise ValueError(
                f"Se necesitan al menos {meses_requeridos} meses de datos históricos. "
                f"Disponibles: {len(datos)}"
            )
        return True
    
    @staticmethod
    def _agregar_por_periodo(pedidos_qs, granularidad='mes'):
        """
        Agrega ventas por período.
        
        Args:
            pedidos_qs: QuerySet de Pedido filtrados
            granularidad: 'dia', 'semana', 'mes', 'año'
        
        Returns:
            pd.Series indexada por fecha con valores de ventas
        """
        from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
        
        trunc_map = {
            'dia': TruncDate,
            'semana': TruncWeek,
            'mes': TruncMonth,
            'año': TruncYear
        }
        
        trunc_func = trunc_map.get(granularidad, TruncMonth)
        
        # Agregar por período
        datos = pedidos_qs.annotate(
            periodo=trunc_func('fecha_creacion')
        ).values('periodo').annotate(
            total=Sum('carrito__total_carrito'),
            cantidad=Count('id')
        ).order_by('periodo')
        
        # Convertir a Series
        df = pd.DataFrame(list(datos))
        if df.empty:
            raise ValueError("No hay datos disponibles para el período seleccionado")
        
        # Rellenar gaps (períodos sin ventas = 0)
        df['periodo'] = pd.to_datetime(df['periodo'])
        df.set_index('periodo', inplace=True)
        
        if granularidad == 'dia':
            freq = 'D'
        elif granularidad == 'semana':
            freq = 'W'
        elif granularidad == 'año':
            freq = 'YS'
        else:  # mes
            freq = 'MS'
        
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq=freq), fill_value=0)
        
        return df['total']
    
    @staticmethod
    def _entrenar_arima(serie_temporal, order=ARIMA_ORDER):
        """
        Entrena modelo ARIMA.
        
        Args:
            serie_temporal: pd.Series de ventas
            order: (p, d, q) tupla de parámetros
        
        Returns:
            ARIMAResults model
        """
        try:
            model = ARIMA(serie_temporal, order=order)
            resultado = model.fit()
            logger.info(f"✅ ARIMA entrenado. AIC: {resultado.aic:.2f}")
            return resultado
        except Exception as e:
            logger.error(f"❌ Error entrenando ARIMA: {str(e)}")
            raise ValueError(f"Error al entrenar modelo: {str(e)}")
    
    @staticmethod
    def _generar_predicciones(modelo_arima, pasos_prediccion, confianza=0.95):
        """
        Genera predicciones con intervalos de confianza.
        
        Returns:
            List[dict] con período, valor, IC inferior, IC superior
        """
        forecast = modelo_arima.get_forecast(steps=pasos_prediccion)
        forecast_df = forecast.conf_int(alpha=1-confianza)
        
        predicciones = []
        for idx, (fecha, fila) in enumerate(forecast_df.iterrows()):
            predicciones.append({
                'periodo': fecha.strftime('%Y-%m'),  # Ajustar según granularidad
                'valor_predicho': float(modelo_arima.fittedvalues.iloc[-1] if idx == 0 else fila.iloc[0]),
                'ic_inferior': max(0, float(fila.iloc[0])),  # No negativos
                'ic_superior': float(fila.iloc[1]),
                'confianza': confianza
            })
        
        return predicciones
    
    @classmethod
    def generar_prediccion(cls, tenant_id=None, config=None):
        """
        Punto de entrada principal para predicciones.
        
        Args:
            tenant_id: ID del tenant (para multi-tenant)
            config: dict con parámetros
                {
                    'data_historica_meses': 24,
                    'prediccion_meses': 12,
                    'granularidad': 'mes',
                    'tipo': 'ventas_totales|por_producto|por_categoria',
                    'producto_id': null,
                    'categoria_id': null
                }
        
        Returns:
            dict con predicciones y métricas
        """
        data_historica = config.get('data_historica_meses', 24)
        prediccion_meses = config.get('prediccion_meses', 12)
        granularidad = config.get('granularidad', 'mes')
        tipo = config.get('tipo', 'ventas_totales')
        
        # Fecha de corte
        ahora = timezone.now()
        fecha_inicio = ahora - timedelta(days=data_historica*30)
        
        # Filtrar pedidos (solo PAGADO)
        pedidos = Pedido.objects.filter(
            estado='PAGADO',
            fecha_creacion__gte=fecha_inicio
        ).select_related('carrito')
        
        if tipo == 'ventas_totales':
            return cls._prediccion_global(
                pedidos, prediccion_meses, granularidad, data_historica
            )
        elif tipo == 'por_producto':
            return cls._prediccion_por_producto(
                pedidos, config.get('producto_id'), prediccion_meses, granularidad
            )
        elif tipo == 'por_categoria':
            return cls._prediccion_por_categoria(
                pedidos, config.get('categoria_id'), prediccion_meses, granularidad
            )
        else:
            raise ValueError(f"Tipo de predicción inválido: {tipo}")
    
    @classmethod
    def _prediccion_global(cls, pedidos_qs, pasos, granularidad, data_historica):
        """Predicción de ventas totales."""
        # Agregar datos
        serie = cls._agregar_por_periodo(pedidos_qs, granularidad)
        
        # Validar datos
        cls._validar_datos_suficientes(serie, cls.MIN_DATA_REQUIRED)
        
        # Entrenar ARIMA
        modelo = cls._entrenar_arima(serie)
        
        # Predecir
        predicciones = cls._generar_predicciones(modelo, pasos)
        
        # Métricas
        metricas = {
            'r_squared': float(modelo.rsquared),
            'aic': float(modelo.aic),
            'rmse': float(np.sqrt(np.mean((modelo.resid) ** 2))),
            'periodo_analisis': f'{data_historica} meses',
            'datos_usados': len(serie),
            'modelo': 'ARIMA(1,1,1)'
        }
        
        return {
            'predicciones': predicciones,
            'historico': [
                {
                    'periodo': fecha.strftime('%Y-%m'),
                    'valor': float(valor)
                }
                for fecha, valor in serie.items()
            ],
            'metricas': metricas,
            'confianza': 0.95
        }
    
    @classmethod
    def _prediccion_por_producto(cls, pedidos_qs, producto_id, pasos, granularidad):
        """Predicción para producto específico."""
        from apps.negocio.ordenes.models.carrito_item import CarritoItem
        
        # Filtrar por producto
        items = CarritoItem.objects.filter(
            carrito__pedido__in=pedidos_qs,
            producto_id=producto_id
        ).values('carrito__pedido__fecha_creacion').annotate(
            total_cantidad=Sum('cantidad'),
            total_vendido=Sum('cantidad') * F('producto__precio')
        )
        
        # Implementación similar a global...
        # (Omitido por brevedad, mismo patrón)
        pass
    
    @classmethod
    def _prediccion_por_categoria(cls, pedidos_qs, categoria_id, pasos, granularidad):
        """Predicción para categoría específica."""
        # Implementación similar...
        pass
    
    @staticmethod
    def validar_configuracion(config):
        """Valida configuración de predicción."""
        errores = []
        
        if config.get('data_historica_meses', 0) < 3:
            errores.append("Mínimo 3 meses de datos históricos")
        
        if config.get('prediccion_meses', 0) > 60:
            errores.append("Máximo 60 meses de predicción")
        
        granularidades_validas = ['dia', 'semana', 'mes', 'año']
        if config.get('granularidad') not in granularidades_validas:
            errores.append(f"Granularidad inválida. Válidas: {granularidades_validas}")
        
        tipos_validos = ['ventas_totales', 'por_producto', 'por_categoria']
        if config.get('tipo') not in tipos_validos:
            errores.append(f"Tipo inválido. Válidos: {tipos_validos}")
        
        return errores
```

---

## 🔌 ViewSet: forecast_views.py

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import HasPermiso
from apps.negocio.reportes.services.forecast_service import ForecastService
from django.core.cache import cache
import json
import hashlib

class PredictionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, HasPermiso]
    required_permiso = 'REP_DINAMICO'
    
    @action(detail=False, methods=['post'], url_path='prediccion')
    def generar_prediccion(self, request):
        """
        POST /api/reportes/prediccion/
        Genera predicción de ventas.
        """
        config = request.data
        
        # Validar configuración
        errores = ForecastService.validar_configuracion(config)
        if errores:
            return Response(
                {'error': 'Configuración inválida', 'detalles': errores},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generar cache key
        cache_key = f"prediccion:{hash(json.dumps(config, sort_keys=True))}"
        
        # Buscar en caché
        resultado_cached = cache.get(cache_key)
        if resultado_cached:
            return Response(resultado_cached)
        
        try:
            # Generar predicción
            resultado = ForecastService.generar_prediccion(
                tenant_id=request.user.tenant_id,
                config=config
            )
            
            # Cachear 24 horas
            cache.set(cache_key, resultado, 86400)
            
            # Registrar en auditoría (opcional)
            self._registrar_auditoria(request.user, config)
            
            return Response(resultado, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error predicción: {str(e)}")
            return Response(
                {'error': 'Error generando predicción'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='prediccion/export-excel')
    def export_excel(self, request):
        """
        POST /api/reportes/prediccion/export-excel/
        Exporta predicción a Excel.
        """
        from apps.negocio.reportes.utils.excel_generator import generar_excel_prediccion
        from django.http import FileResponse
        
        try:
            datos = request.data
            archivo = generar_excel_prediccion(datos)
            
            return FileResponse(
                archivo,
                as_attachment=True,
                filename=f"prediccion_ventas_{timezone.now().date()}.xlsx"
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='prediccion/productos')
    def listar_productos(self, request):
        """
        GET /api/reportes/prediccion/productos/
        Lista productos para selector.
        """
        productos = Producto.objects.filter(
            activo=True
        ).values('id', 'nombre', 'sku').order_by('nombre')
        
        return Response(list(productos))
    
    def _registrar_auditoria(self, usuario, config):
        """Registra generación de predicción en auditoría."""
        try:
            from apps.customers.audits.models.auditoria import Auditoria
            Auditoria.objects.create(
                usuario=usuario,
                accion='GENERAR_PREDICCION',
                tabla='reportes_prediccion',
                detalles=json.dumps(config),
                ip_origen=self._obtener_ip(self.request)
            )
        except Exception as e:
            logger.warning(f"Error registrando auditoría: {str(e)}")
    
    @staticmethod
    def _obtener_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
```

---

## 📄 Modelo: prediccion_cache.py

```python
from django.db import models
from django.contrib.auth.models import User

class PredictionCache(models.Model):
    """Caché de predicciones generadas."""
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    configuracion = models.JSONField(verbose_name="Configuración")
    resultado = models.JSONField(verbose_name="Resultado predicción")
    hash_config = models.CharField(max_length=64, unique=True, db_index=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(verbose_name="Expira a las")
    vigente = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'app_negocio_prediction_cache'
        verbose_name = 'Caché Predicción'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Predicción {self.usuario} - {self.fecha_creacion}"
```

---

## 📊 Utilidad: excel_generator.py

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from io import BytesIO
from datetime import datetime

def generar_excel_prediccion(datos):
    """Genera archivo Excel con predicción."""
    
    wb = Workbook()
    
    # Hoja 1: Predicción
    ws1 = wb.active
    ws1.title = "Predicción"
    
    # Encabezados
    encabezados = ["Período", "Histórico", "Predicho", "IC Inferior", "IC Superior", "Confianza"]
    ws1.append(encabezados)
    
    # Estilo encabezados
    for cell in ws1[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
    
    # Datos
    for pred in datos['predicciones']:
        ws1.append([
            pred['periodo'],
            pred.get('valor_historico', ''),
            pred['valor_predicho'],
            pred['ic_inferior'],
            pred['ic_superior'],
            f"{pred['confianza']*100:.1f}%"
        ])
    
    # Ancho columnas
    for col in ['A', 'B', 'C', 'D', 'E', 'F']:
        ws1.column_dimensions[col].width = 15
    
    # Hoja 2: Métricas
    ws2 = wb.create_sheet("Métricas")
    
    metricas = datos.get('metricas', {})
    ws2.append(["Métrica", "Valor"])
    
    for clave, valor in metricas.items():
        if isinstance(valor, float):
            valor = f"{valor:.4f}"
        ws2.append([clave.replace('_', ' ').title(), valor])
    
    # Hoja 3: Info
    ws3 = wb.create_sheet("Info")
    ws3.append(["Generado", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    ws3.append(["Confianza", f"{datos.get('confianza', 0.95)*100:.1f}%"])
    ws3.append(["Datos históricos", f"{len(datos.get('historico', []))} períodos"])
    
    # Convertir a bytes
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return buffer
```

---

## 🔗 URLs: actualizar urls.py

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .forecast_views import PredictionViewSet

router = DefaultRouter()
router.register('prediccion', PredictionViewSet, basename='prediccion')

urlpatterns = [
    path('', include(router.urls)),
]
```

---

## 📋 REQUIREMENTS: Agregar a requirements/base.txt

```txt
statsmodels==0.14.0    # Para ARIMA
openpyxl==3.11.0       # Para Excel
```

**Instalación:**
```bash
pip install statsmodels==0.14.0 openpyxl==3.11.0
```

---

## 🗄️ MIGRACIÓN Django

```bash
python manage.py makemigrations reportes
python manage.py migrate reportes
```

---

## 📊 FLUJO DE EJECUCIÓN

```
1. Frontend POST /api/reportes/prediccion/
   {
     "data_historica_meses": 24,
     "prediccion_meses": 12,
     "granularidad": "mes",
     "tipo": "ventas_totales"
   }

2. PredictionViewSet.generar_prediccion()
   ├─ Validar config
   ├─ Buscar cache
   └─ Si no existe:
      └─ ForecastService.generar_prediccion()
         ├─ Filtrar Pedidos (últimos 24 meses, estado PAGADO)
         ├─ Agregar por mes
         ├─ Validar >= 3 meses
         ├─ Entrenar ARIMA(1,1,1)
         ├─ Generar 12 predicciones
         └─ Retornar {predicciones, histórico, métricas}

3. Cachear resultado (24h)

4. Registrar auditoría

5. Retornar respuesta a Frontend
```

---

## 🧪 TESTING

```python
# tests/test_forecast.py
from django.test import TestCase
from apps.negocio.reportes.services.forecast_service import ForecastService
from apps.negocio.ordenes.models.pedido import Pedido
import pandas as pd

class ForecastServiceTest(TestCase):
    def test_validar_datos_suficientes(self):
        """Debe rechazar < 3 meses."""
        serie = pd.Series([1000, 1200])
        with self.assertRaises(ValueError):
            ForecastService._validar_datos_suficientes(serie, 3)
    
    def test_generar_prediccion_exitosa(self):
        """Debe generar predicción con datos válidos."""
        # Crear datos de prueba...
        # ...
        pass
```

---

## ✅ CHECKLIST

- [ ] Instalar dependencias (statsmodels, openpyxl)
- [ ] Crear forecast_service.py
- [ ] Crear forecast_views.py
- [ ] Crear prediccion_cache.py
- [ ] Crear excel_generator.py
- [ ] Actualizar urls.py
- [ ] Crear y ejecutar migración
- [ ] Agregar permiso `REP_DINAMICO` en seed_permisos.py
- [ ] Testing unitario
- [ ] Testing integración con Frontend
- [ ] Documentación de APIs
- [ ] Performance test (con muchos datos)

---

## 🚀 OPTIMIZACIONES (Futuro)

1. **Auto-detección de orden ARIMA** usando auto_arima
2. **Múltiples modelos** (SARIMA para estacionalidad)
3. **Predicción ensemble** (promedio múltiples modelos)
4. **Alertas automáticas** cuando predicción cae > 20%
5. **ML avanzado**: Prophet, LightGBM para series más complejas

