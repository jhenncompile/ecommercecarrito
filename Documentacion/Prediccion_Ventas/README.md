# 📊 MÓDULO DE PREDICCIÓN DE VENTAS - DOCUMENTACIÓN COMPLETA

## 📌 Descripción del Módulo

Sistema de estimación de ventas con inteligencia artificial usando modelos ARIMA para el análisis de series temporales. Permite a los vendedores estimar la **cantidad futura de ventas/unidades vendidas** basándose en históricos de 3 meses hasta 2 años, con visualizaciones en gráficas interactivas y exportación de reportes.

El monto económico debe tratarse como **referencial**: cuando aplique, se calcula usando la cantidad estimada y el precio actual del producto. La interfaz y los reportes deben mostrar el disclaimer: "Monto referencial calculado con precios actuales. Si los precios cambian, el monto estimado también cambiará."

---

## 🎯 Enfoque Funcional

- **Métrica principal:** cantidad estimada de ventas, pedidos cobrados o unidades vendidas.
- **Métrica secundaria:** monto estimado referencial calculado con precios actuales.
- **Tono del módulo:** usar "estimación" en lugar de prometer predicciones exactas.
- **Fuente sugerida:** ventas cobradas/finalizadas, excluyendo pedidos pendientes o cancelados.
- **Uso esperado:** planificación de inventario, reabastecimiento y campañas de marketing.

---

## 📑 ÍNDICE DE DOCUMENTACIÓN

### 1. **📖 [Historias de Usuario](./01_Historias_Usuario.md)**
   - **Contenido:** Definición completa de 20 historias de usuario distribuidas en Frontend, Backend y Móvil
   - **Para:** Product Owners, QA, Developers para entender requisitos
   - **Descargar:** Tabla resumen en Excel con HUs, criterios y prioridades
   - **Secciones:**
     - HUs Frontend (6 historias)
     - HUs Backend (7 historias)
     - HUs Móvil (5 historias)
     - HUs Integración (2 historias)

---

### 2. **💻 [Implementación Frontend](./02_Implementacion_Frontend.md)**
   - **Contenido:** Arquitectura React, componentes detallados, estilos, hooks, integración
   - **Para:** Desarrolladores Frontend, Diseñadores UX
   - **Descargar:** Capturas de UI, paleta de colores, wireframes
   - **Secciones:**
     - Estructura de carpetas
     - 6 Componentes principales (Filters, Chart, Table, ProductSelector, ExportButtons, Main)
     - Hook reutilizable (usePrediction)
     - Estilos (Predicciones.module.css)
     - API endpoints esperados
     - Responsive design
     - Checklist de desarrollo

---

### 3. **⚙️ [Implementación Backend](./03_Implementacion_Backend.md)**
   - **Contenido:** Servicio ARIMA, ViewSet REST, modelos, exportación Excel, caché
   - **Para:** Desarrolladores Backend, DevOps
   - **Descargar:** Código fuente comentado, queries SQL de ejemplo, test unitarios
   - **Secciones:**
     - Estructura de carpetas
     - ForecastService (ARIMA logic)
     - PredictionViewSet (REST APIs)
     - Modelos Django
     - Excel generator
     - URLs y migraciones
     - Requisitos pip (statsmodels, openpyxl)
     - Testing
     - Optimizaciones futuras

---

### 4. **📱 [Implementación Móvil](./04_Implementacion_Movil.md)**
   - **Contenido:** Arquitectura Flutter, BLoC pattern, widgets, servicios
   - **Para:** Desarrolladores Móvil
   - **Descargar:** Código Flutter completo, dependencias, estructura CLEAN
   - **Secciones:**
     - Estructura CLEAN (Data, Domain, Presentation)
     - Modelos Dart (Prediccion, ForecastRequest, ForecastResponse)
     - Remote DataSource
     - Repository pattern
     - BLoC (events, states)
     - Widgets (Chart, Table, Filters, Export)
     - Servicios (File, Notificaciones)
     - pubspec.yaml
     - Responsive design

---

## 📊 DESCARGAS DISPONIBLES

### Para Descargar TABLAS → EXCEL:

1. **Tabla de Historias de Usuario** (HUs)
   - Formato: `.xlsx`
   - Incluye: ID | Descripción | Frontend | Backend | Móvil | Prioridad | Criterios Aceptación
   - Archivo: [descargar_HUs.xlsx](#)

2. **Tabla de Componentes Frontend**
   - Formato: `.xlsx`
   - Incluye: Componente | Responsabilidad | Props | Estado interno | Dependencias
   - Archivo: [descargar_Componentes_FE.xlsx](#)

3. **Tabla de Endpoints Backend**
   - Formato: `.xlsx`
   - Incluye: Endpoint | Método | Parámetros | Response | Errors
   - Archivo: [descargar_APIs_Backend.xlsx](#)

4. **Tabla de Modelos Dart (Móvil)**
   - Formato: `.xlsx`
   - Incluye: Modelo | Atributos | Métodos | Serializacion
   - Archivo: [descargar_Modelos_Movil.xlsx](#)

5. **Tabla de Librerías/Dependencias**
   - Formato: `.xlsx`
   - Incluye: Frontend (npm) | Backend (pip) | Móvil (pub.dev) | Versiones
   - Archivo: [descargar_Dependencias.xlsx](#)

---

### Para Descargar GRÁFICOS → IMÁGENES:

1. **Mockups UI Frontend**
   - Formato: `.png` (1920x1080)
   - Incluye: 
     - Dashboard principal
     - Filtros desplegables
     - Gráfica con predicción
     - Tabla de datos
     - Modal de exportación
   - Carpeta: [descargar_Mockups_UI.zip](#)

2. **Diagrama de Arquitectura**
   - Formato: `.png` (2560x1440)
   - Incluye: Flujo Frontend → Backend → BD
   - Archivo: [descargar_Arquitectura.png](#)

3. **Diagrama de Flujo de Datos**
   - Formato: `.png` (1920x1080)
   - Incluye: Request → Predicción → Response
   - Archivo: [descargar_Flujo_Datos.png](#)

4. **Gráficos Técnicos**
   - Formato: `.png`
   - Incluye:
     - Estructura de carpetas (Frontend, Backend, Móvil)
     - Diagrama BLoC
     - Modelo ARIMA flow
   - Carpeta: [descargar_Diagramas_Tecnicos.zip](#)

5. **Paleta de Colores**
   - Formato: `.png` (1024x768)
   - Incluye: Colores del proyecto con valores HEX/RGB
   - Archivo: [descargar_Paleta_Colores.png](#)

---

## 🏗️ ARQUITECTURA GENERAL

```
PREDICCIÓN DE VENTAS
│
├── FRONTEND (React)
│   ├── PredictionFilters (Entrada)
│   ├── PredictionChart (Visualización)
│   ├── PredictionTable (Datos)
│   └── ExportButtons (Salida)
│
├── BACKEND (Django REST)
│   ├── PredictionViewSet (API)
│   ├── ForecastService (ARIMA)
│   ├── ExcelGenerator (Exportar)
│   └── Cache (Performance)
│
└── MÓVIL (Flutter)
    ├── PredictionBloc (State)
    ├── PredictionChart (fl_chart)
    ├── PredictionTable (DataTable)
    └── FileService (Descargas)
```

---

## 🎯 OBJETIVOS ALCANZADOS

✅ Estimación de cantidad futura de ventas/unidades (1-24 meses)
✅ Monto estimado referencial basado en precios actuales
✅ Análisis histórico flexible (3 meses - 2 años)
✅ Granularidad configurable (día, semana, mes, año)
✅ Múltiples tipos de análisis (global, por producto, por categoría)
✅ Gráficas interactivas con Chart.js y fl_chart
✅ Exportación a Excel con estilos
✅ Exportación de gráficas como PNG
✅ Multi-tenant completo
✅ Permisos RBAC integrados
✅ Auditoría de reportes generados
✅ Caché de predicciones (24h)
✅ Responsive design (móvil, tablet, desktop)

---

## 🚀 PRÓXIMOS PASOS

1. **Fase 1 - Backend Fundacional** (2 semanas)
   - Implementar ForecastService
   - Crear PredictionViewSet
   - Testing unitario

2. **Fase 2 - Frontend Base** (2 semanas)
   - Componentes React
   - Gráfica Chart.js
   - Integración API

3. **Fase 3 - Móvil** (2 semanas)
   - BLoC pattern
   - Widgets Flutter
   - Testing

4. **Fase 4 - Pulido** (1 semana)
   - Optimizaciones
   - Testing E2E
   - Deploy

---

## 📋 TABLA RESUMEN GENERAL

| Aspecto | Detalles |
|--------|----------|
| **Historias de Usuario** | 20 HUs (Frontend 6, Backend 7, Móvil 5, Integración 2) |
| **Componentes Frontend** | 6 componentes React |
| **Endpoints Backend** | 3 endpoints REST principales |
| **Modelos Backend** | 2 modelos (PredictionCache, + actualizar Pedido) |
| **Widgets Móvil** | 5 widgets Flutter |
| **Métrica Principal** | Cantidad de ventas/pedidos cobrados o unidades vendidas |
| **Monto Estimado** | Referencial, calculado con precios actuales |
| **Algoritmo** | ARIMA(1,1,1) para series temporales de cantidades |
| **Librerías Nuevas** | statsmodels, openpyxl, fl_chart, share_plus |
| **Caché** | Redis 24h |
| **Exportación** | Excel (.xlsx) + PNG (gráficas) |
| **Permisos** | REP_DINAMICO (ya existe) |
| **Multi-tenant** | ✅ Completo |
| **Auditoría** | ✅ Registra cada predicción generada |

---

## 📞 CONTACTO & NOTAS

- **Documentación generada:** 31 de Mayo de 2026
- **Estado:** 📋 Pronto para implementación
- **Dependencias externas:** statsmodels, openpyxl (backend), fl_chart (móvil)
- **Estimado:** 4-6 semanas desarrollo
- **Testing:** Unit, Integration, E2E recomendado

---

## 🎓 CÓMO USAR ESTA DOCUMENTACIÓN

### Para Product Owners:
→ Lee [01_Historias_Usuario.md](./01_Historias_Usuario.md) (secciones de HU)

### Para Desarrolladores Frontend:
→ Lee [02_Implementacion_Frontend.md](./02_Implementacion_Frontend.md)

### Para Desarrolladores Backend:
→ Lee [03_Implementacion_Backend.md](./03_Implementacion_Backend.md)

### Para Desarrolladores Móvil:
→ Lee [04_Implementacion_Movil.md](./04_Implementacion_Movil.md)

### Para Descargar Archivos:
→ Ve a sección [Descargas Disponibles](#descargas-disponibles) arriba

---

## 🔒 SEGURIDAD & PRIVACIDAD

- ✅ Autenticación JWT obligatoria
- ✅ Permiso `REP_DINAMICO` requerido
- ✅ Multi-tenant completamente aislado
- ✅ Auditoría de todas las predicciones
- ✅ Caché no almacena datos sensibles
- ✅ Excel/PNG sin información de usuario

---

## 📞 SOPORTE

Para dudas sobre:
- **Funcionalidad:** Revisar HUs correspondientes
- **Código:** Revisar sección de implementación
- **APIs:** Ver tabla de endpoints en Backend doc
- **UI/UX:** Ver mockups descargables

---

**📅 Última actualización:** 31 Mayo 2026
**✍️ Autor:** Equipo de Desarrollo
**📌 Estado:** PRONTO PARA IMPLEMENTACIÓN

