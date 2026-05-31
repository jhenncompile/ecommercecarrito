# Historias de Usuario - Módulo de Predicción de Ventas

## Enfoque del Módulo

El módulo debe presentar **estimaciones**, no valores garantizados. La métrica principal será la **cantidad esperada de ventas/unidades vendidas**, porque el monto histórico puede distorsionarse si los precios de productos cambian con el tiempo.

- **Predicción global:** estimar cantidad de ventas/pedidos cobrados por período.
- **Predicción por producto:** estimar unidades vendidas por período.
- **Predicción por categoría:** estimar unidades vendidas por período dentro de la categoría.
- **Monto estimado referencial:** cuando aplique, calcularlo usando la cantidad estimada y el precio actual del producto. Debe mostrarse con el disclaimer: "Monto referencial calculado con precios actuales. Si los precios cambian, el monto estimado también cambiará."

---

## 📱 FRONTEND

### HU-001: Visualizar Dashboard de Predicciones
**Como** vendedor, **quiero** acceder a un dashboard con estimaciones de cantidad de ventas, **para** tomar decisiones sobre inventario, reabastecimiento y marketing.

- **Criterios de Aceptación:**
  - [x] Acceso desde menú principal → "Reportes" → Tab "Predicciones"
  - [x] Interfaz limpia con filtros visibles
  - [x] Carga de datos sin bloquear UI
  - [x] Manejo de errores con mensajes amigables
  - [x] Mostrar la cantidad estimada como métrica principal
  - [x] Mostrar monto estimado referencial cuando exista precio actual aplicable
  - [x] Mostrar disclaimer indicando que el monto depende de precios actuales

- **Datos Requeridos:**
  - Período histórico (6m, 1y, 2y, Todo)
  - Período predicción (1m, 3m, 6m, 1y, 2y)
  - Granularidad (Día, Semana, Mes, Año)
  - Tipo (Global, Por Producto, Por Categoría)
  - Métrica principal: Cantidad de ventas/unidades
  - Monto referencial: Calculado con precio actual del producto cuando aplique

---

### HU-002: Generar Gráfica de Predicción
**Como** vendedor, **quiero** ver una gráfica interactiva de estimaciones de cantidad, **para** visualizar tendencias futuras.

- **Criterios de Aceptación:**
  - [x] Gráfica de línea con Chart.js
  - [x] Área sombreada diferenciando histórico vs predicción
  - [x] Intervalo de confianza (zona gris alrededor de la línea)
  - [x] Tooltip interactivo al pasar mouse
  - [x] Leyenda clara (Histórico, Predicción, IC inferior, IC superior)
  - [x] Responsive en móvil

- **Elementos Visuales:**
  - Línea azul: Cantidad histórica
  - Línea roja punteada: Cantidad estimada
  - Área sombreada: Intervalo de confianza 95%
  - Colores accesibles (alto contraste)
  - Texto auxiliar: "Estimación basada en histórico; no representa garantía de ventas"

---

### HU-003: Exportar Reporte de Predicción
**Como** vendedor, **quiero** descargar el reporte en Excel, **para** compartirlo con mi equipo.

- **Criterios de Aceptación:**
  - [x] Botón "Descargar Excel" en la vista
  - [x] Archivo .xlsx con columnas: Período | Cantidad Histórica | Cantidad Estimada | Precio Actual | Monto Estimado Referencial | IC Inferior | IC Superior | Confianza
  - [x] Formato profesional con estilos
  - [x] Nombre archivo: `prediccion_ventas_YYYY-MM-DD.xlsx`
  - [x] Validación: No permitir descarga si no hay datos
  - [x] Incluir nota: "Monto referencial calculado con precios actuales"

---

### HU-004: Filtrar Predicciones por Producto
**Como** vendedor, **quiero** ver la cantidad estimada de ventas de un producto específico, **para** planificar reorden de ese producto.

- **Criterios de Aceptación:**
  - [x] Selector dropdown con lista de productos activos
  - [x] Búsqueda en tiempo real dentro del dropdown
  - [x] Mostrar gráfica + tabla específica del producto
  - [x] Indicador de tendencia (↑↓)
  - [x] Alert si producto tiene < 3 meses de datos
  - [x] Mostrar monto estimado referencial calculado con el precio actual del producto
  - [x] Mostrar disclaimer si el precio actual se usa para calcular monto

---

### HU-005: Comparar Múltiples Productos
**Como** vendedor, **quiero** comparar predicciones de varios productos en una sola gráfica, **para** identificar patrones.

- **Criterios de Aceptación:**
  - [x] Multi-select de productos (máx 5)
  - [x] Gráficas superpuestas con colores distintos
  - [x] Leyenda con toggle on/off para cada producto
  - [x] Tabla comparativa

---

### HU-006: Descargar Gráficas como Imágenes
**Como** vendedor, **quiero** descargar la gráfica como PNG/JPG, **para** incluirla en presentaciones.

- **Criterios de Aceptación:**
  - [x] Botón "Descargar Gráfica" (icono camera)
  - [x] Formato PNG con resolución 1920x1080
  - [x] Incluir título, datos, fecha generación
  - [x] Nombre: `prediccion_grafica_YYYY-MM-DD.png`

---

## 🔧 BACKEND

### HU-007: Crear Endpoint de Predicción
**Como** desarrollador, **quiero** un endpoint REST `/api/reportes/prediccion/`, **para** que frontend pueda solicitar predicciones.

- **Criterios de Aceptación:**
  - [x] Método POST con validación de permisos (`REP_DINAMICO`)
  - [x] Request body:
    ```json
    {
      "data_historica_meses": 24,
      "prediccion_meses": 12,
      "granularidad": "mes",
      "tipo": "ventas_cantidad",
      "producto_id": null,
      "categoria_id": null
    }
    ```
  - [x] Response con cantidades estimadas + metadata
  - [x] Response puede incluir monto estimado referencial calculado con precios actuales
  - [x] Manejo de errores (datos insuficientes, permiso denegado, etc.)

---

### HU-008: Generar Predicción con ARIMA
**Como** backend, **quiero** entrenar modelo ARIMA sobre cantidades históricas, **para** generar estimaciones futuras.

- **Criterios de Aceptación:**
  - [x] Usar `statsmodels.tsa.arima.ARIMA`
  - [x] Validar datos mínimos (3 meses históricos)
  - [x] Auto-detección de orden (p, d, q) o manual
  - [x] Generar intervalos de confianza 95%
  - [x] Retornar cantidades estimadas + métricas (AIC, R²)
  - [x] Retornar monto estimado referencial cuando exista precio actual aplicable
  - [x] Manejo de excepciones (convergencia, datos insuficientes)

- **Salida:**
  ```python
  {
    "predicciones": [
      {
        "periodo": "2026-06",
        "cantidad_estimada": 42,
        "ic_inferior": 36,
        "ic_superior": 48,
        "precio_actual": 120.00,
        "monto_estimado_referencial": 5040.00,
        "confianza": 0.95,
        "nota": "Monto referencial calculado con precios actuales. Si los precios cambian, el monto estimado también cambiará."
      }
    ],
    "metricas": {
      "r_squared": 0.87,
      "aic": 1234.56,
      "rmse": 1200.45
    }
  }
  ```

---

### HU-009: Agregar Datos por Período
**Como** backend, **quiero** agregar cantidades vendidas por granularidad, **para** ajustar la estimación a nivel día/semana/mes.

- **Criterios de Aceptación:**
  - [x] Función `agregar_ventas(pedidos_qs, granularidad: str)`
  - [x] Soportar: día, semana, mes, año
  - [x] Retornar Series de pandas indexada por fecha
  - [x] Manejar períodos sin ventas (rellenar con 0 o interpolar)

---

### HU-010: Validar Datos Históricos Suficientes
**Como** backend, **quiero** validar que hay datos suficientes, **para** no entrenar con poco histórico.

- **Criterios de Aceptación:**
  - [x] Mínimo requerido: 3 meses de datos
  - [x] Error si `len(datos_historicos) < periodo_requerido`
  - [x] Mensajes claros: "Se necesitan al menos X meses de datos"

---

### HU-011: Generar Predicción por Producto
**Como** backend, **quiero** predecir ventas individuales por producto, **para** análisis de SKU.

- **Criterios de Aceptación:**
  - [x] Filtrar Pedidos → CarritoItem por producto
  - [x] Agregar cantidad vendida por período
  - [x] Entrenar ARIMA individual
  - [x] Retornar predicciones + confianza

---

### HU-012: Cachear Predicciones
**Como** backend, **quiero** cachear resultados de predicción, **para** mejorar performance.

- **Criterios de Aceptación:**
  - [x] TTL: 24 horas
  - [x] Cache key: `prediction:{tenant_id}:{tipo}:{granularidad}:{producto_id}`
  - [x] Invalidar cache si hay nuevo pedido en intervalo

---

### HU-013: Generar Reporte Excel
**Como** backend, **quiero** crear archivo Excel, **para** descargar reportes.

- **Criterios de Aceptación:**
  - [x] Usar `openpyxl` o `pandas.ExcelWriter`
  - [x] Hoja 1: Tabla predicción (Período | Cantidad Histórica | Cantidad Estimada | Precio Actual | Monto Referencial | IC | Confianza)
  - [x] Hoja 2: Métricas modelo (R², RMSE, AIC)
  - [x] Hoja 3: Metadata (Fecha generación, período análisis, usuario, disclaimer de monto referencial)
  - [x] Estilos: encabezados negrita, números formateados

---

## 📱 MÓVIL (Flutter)

### HU-014: Acceder a Predicciones desde App
**Como** vendedor en móvil, **quiero** ver predicciones de ventas, **para** consultar en cualquier lugar.

- **Criterios de Aceptación:**
  - [x] Acceso desde drawer → "Analytics" → "Predicciones"
  - [x] Interfaz adaptada a pantalla pequeña
  - [x] Scroll vertical para ver tabla
  - [x] Funciona offline (últimas predicciones en caché local)

---

### HU-015: Gráfica de Predicción en Móvil
**Como** vendedor, **quiero** ver gráfica en pantalla móvil, **para** visualizar tendencias rápidamente.

- **Criterios de Aceptación:**
  - [x] Usar `fl_chart` para gráficas
  - [x] Gráfica de línea responsiva
  - [x] Zoom/scroll en gráfica
  - [x] Tooltip al tocar
  - [x] Leyenda colapsable

---

### HU-016: Descargar Reporte en Móvil
**Como** vendedor, **quiero** descargar Excel desde móvil, **para** compartir vía email/WhatsApp.

- **Criterios de Aceptación:**
  - [x] Botón "Descargar" en bottom sheet
  - [x] Crear archivo en directorio Downloads
  - [x] Share intent: permitir enviar a email, Drive, etc.
  - [x] Notificación de descarga completada

---

### HU-017: Filtros en Móvil
**Como** vendedor, **quiero** filtrar por periodo/producto/granularidad en móvil, **para** realizar análisis específicos.

- **Criterios de Aceptación:**
  - [x] Bottom sheet desplegable con filtros
  - [x] Compact layout (no ocupar mucho espacio)
  - [x] Guardar últimos filtros usados

---

### HU-018: Push Notification de Predicciones
**Como** vendedor, **quiero** recibir alerta si la estimación indica caída en cantidad de ventas, **para** tomar acción proactiva.

- **Criterios de Aceptación:**
  - [x] Configurar notificaciones en Settings
  - [x] Alerta si cantidad estimada del próximo mes cae > 20%
  - [x] Mensaje: "Predicción: la cantidad de ventas podría caer 30% en Junio"
  - [x] Deep link al reporte de predicciones

---

## 🔗 INTEGRACIÓN MULTI-TENANT

### HU-019: Aislar Predicciones por Tenant
**Como** sistema, **quiero** que cada tenant tenga predicciones solo de sus datos, **para** mantener privacidad.

- **Criterios de Aceptación:**
  - [x] Filtrar Pedidos por tenant_id en query
  - [x] Usar `schema_context` en multi-tenant
  - [x] Validar permiso de usuario dentro del tenant
  - [x] Test: Tenant A no ve datos de Tenant B

---

### HU-020: Auditar Generación de Reportes
**Como** admin, **quiero** registrar qué usuario generó qué reporte, **para** auditoría.

- **Criterios de Aceptación:**
  - [x] Log en tabla Auditoria: usuario, fecha, tipo predicción, parámetros
  - [x] API para consultar historial de reportes por usuario
  - [x] Retención: 6 meses

---

## 📊 TABLA RESUMEN DE HUs

| ID | Descripción | Frontend | Backend | Móvil | Prioridad |
|----|-------------|----------|---------|-------|-----------|
| HU-001 | Dashboard | ✅ | ✅ | ✅ | ALTA |
| HU-002 | Gráfica | ✅ | ⚪ | ✅ | ALTA |
| HU-003 | Exportar Excel | ✅ | ✅ | ✅ | MEDIA |
| HU-004 | Filtrar Producto | ✅ | ✅ | ✅ | MEDIA |
| HU-005 | Comparar Productos | ✅ | ✅ | ⚪ | BAJA |
| HU-006 | Descargar Gráfica | ✅ | ⚪ | ⚪ | BAJA |
| HU-007 | Endpoint | ⚪ | ✅ | ⚪ | ALTA |
| HU-008 | ARIMA sobre cantidades | ⚪ | ✅ | ⚪ | ALTA |
| HU-009 | Agregar cantidades | ⚪ | ✅ | ⚪ | ALTA |
| HU-010 | Validar | ⚪ | ✅ | ⚪ | ALTA |
| HU-011 | Pred. Producto | ⚪ | ✅ | ⚪ | MEDIA |
| HU-012 | Cache | ⚪ | ✅ | ⚪ | MEDIA |
| HU-013 | Excel | ⚪ | ✅ | ⚪ | MEDIA |
| HU-014 | Acceso Móvil | ⚪ | ⚪ | ✅ | MEDIA |
| HU-015 | Gráfica Móvil | ⚪ | ⚪ | ✅ | MEDIA |
| HU-016 | Descargar Móvil | ⚪ | ⚪ | ✅ | MEDIA |
| HU-017 | Filtros Móvil | ⚪ | ⚪ | ✅ | MEDIA |
| HU-018 | Notificaciones | ⚪ | ✅ | ✅ | BAJA |
| HU-019 | Multi-tenant | ⚪ | ✅ | ⚪ | ALTA |
| HU-020 | Auditoría | ⚪ | ✅ | ⚪ | MEDIA |

---

## 📈 Dependencias

```
HU-007, HU-008, HU-009, HU-010 (Backend)
    ↓
HU-001, HU-002, HU-003, HU-004 (Frontend)
    ↓
HU-005, HU-006 (Frontend avanzado)
    ↓
HU-014, HU-015, HU-016 (Móvil)
```

**Sugerencia:** Implementar primero HUs ALTA prioridad (Backend fundacional), luego Frontend base, luego extensiones y Móvil.
