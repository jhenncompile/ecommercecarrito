import numpy as np
import pandas as pd
from django.db import connection
from django.db.models import Sum, Count, Max, Q
from django.utils import timezone
from apps.customers.clientes.models.cliente import Cliente
from apps.negocio.billing.models import Factura, DetalleFactura

class CustomerBehaviorService:

    @classmethod
    def obtener_analisis_comportamiento(cls):
        now = timezone.now().date()
        
        # 1. TASA DE REPETICIÓN DE COMPRA
        compras_por_cliente = Factura.objects.filter(
            estado='VIGENTE'
        ).values('cliente_id').annotate(
            num_compras=Count('nro')
        )
        
        total_compradores = len(compras_por_cliente)
        compradores_recurrentes = sum(1 for c in compras_por_cliente if c['num_compras'] > 1)
        
        tasa_repeticion = (compradores_recurrentes / total_compradores * 100) if total_compradores > 0 else 0.0

        # 2. CALCULAR RFM BASADO EN FACTURAS VIGENTES
        rfm_datos = Factura.objects.filter(
            estado='VIGENTE'
        ).values('cliente_id').annotate(
            ultima_compra=Max('fecha'),
            frecuencia=Count('nro', distinct=True),
            valor_monetario=Sum('monto_total')
        )
        
        # Mapear de manera segura los clientes globales
        clientes_map = {c.id: c for c in Cliente.objects.all()}
        
        compradores_list = []
        compradores_ids = set()
        
        for rfm in rfm_datos:
            cliente_id = rfm['cliente_id']
            cliente_obj = clientes_map.get(cliente_id)
            if cliente_obj:
                compradores_ids.add(cliente_id)
                recencia = (now - rfm['ultima_compra']).days if rfm['ultima_compra'] else 9999
                compradores_list.append({
                    "cliente_id": cliente_id,
                    "nombre": cliente_obj.nombre,
                    "correo": cliente_obj.correo,
                    "recencia": recencia,
                    "frecuencia": rfm['frecuencia'],
                    "monetario": float(rfm['valor_monetario'] or 0.0)
                })
                
        no_compradores_list = []
        for c_id, c_obj in clientes_map.items():
            if c_id not in compradores_ids:
                no_compradores_list.append({
                    "cliente_id": c_id,
                    "nombre": c_obj.nombre,
                    "correo": c_obj.correo,
                    "recencia": None,
                    "frecuencia": 0,
                    "monetario": 0.0,
                    "segmento": "Sin Compras"
                })

        # 3. SEGMENTACIÓN DE COMPORTAMIENTO CON K-MEANS (sklearn)
        # Solo ejecutamos si hay suficientes compradores
        if len(compradores_list) > 0:
            df = pd.DataFrame(compradores_list)
            
            # Número de clusters adaptativo según cantidad de datos
            n_clusters = min(4, len(compradores_list))
            
            if n_clusters >= 2:
                # Lazy import de sklearn
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler
                
                # Normalizar métricas RFM
                scaler = StandardScaler()
                rfm_scaled = scaler.fit_transform(df[['recencia', 'frecuencia', 'monetario']])
                
                # Ejecutar K-Means
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
                df['cluster'] = kmeans.fit_predict(rfm_scaled)
                
                # Para etiquetar inteligentemente (VIP, Fiel, etc.), rankeamos los clusters
                # Calculamos el promedio de frecuencia y monto de cada cluster, y restamos la recencia promedio
                cluster_stats = df.groupby('cluster').agg({
                    'recencia': 'mean',
                    'frecuencia': 'mean',
                    'monetario': 'mean'
                })
                
                # Score para rankear clusters:
                # - Recencia en dias: MENOS dias = MEJOR (cliente reciente). Penalizamos x3.
                # - Frecuencia: MAS compras = MEJOR. Premiamos x2.
                # - Monetario: MAS gasto = MEJOR. Premiamos x2.
                # La recencia tiene el mayor peso negativo para que un cliente
                # con 124+ dias de inactividad NO pueda ser clasificado como Fiel,
                # sin importar cuantas compras haya hecho en el pasado.
                max_rec = cluster_stats['recencia'].max() or 1
                max_freq = cluster_stats['frecuencia'].max() or 1
                max_mon = cluster_stats['monetario'].max() or 1
                
                cluster_stats['score'] = (
                    (cluster_stats['frecuencia'] / max_freq) * 2 +
                    (cluster_stats['monetario'] / max_mon) * 2 -
                    (cluster_stats['recencia'] / max_rec) * 3
                )
                
                # Ordenar clusters por score descendente
                sorted_clusters = cluster_stats.sort_values(by='score', ascending=False).index.tolist()
                
                # Mapeo de nombres según rango
                nombres_segmentos = ["VIP / Campeón", "Fiel / Frecuente", "Prometedor / Nuevo", "En Riesgo / Inactivo"]
                segment_mapping = {sorted_clusters[i]: nombres_segmentos[min(i, len(nombres_segmentos)-1)] for i in range(len(sorted_clusters))}
                
                df['segmento'] = df['cluster'].map(segment_mapping)
            else:
                # Si solo hay 1 comprador, se le asigna segmento base
                df['segmento'] = "Cliente Activo"
                
            compradores_list = []
            for _, row in df.iterrows():
                compradores_list.append({
                    "cliente_id": int(row["cliente_id"]),
                    "nombre": str(row["nombre"]),
                    "correo": str(row["correo"]),
                    "recencia": int(row["recencia"]),
                    "frecuencia": int(row["frecuencia"]),
                    "monetario": float(row["monetario"]),
                    "segmento": str(row["segmento"])
                })

        # Unir todos los clientes
        todos_clientes = compradores_list + no_compradores_list

        # 4. INTERESES POR CATEGORÍA
        preferencias_categorias = DetalleFactura.objects.filter(
            factura__estado='VIGENTE'
        ).values(
            'producto__categoria__nombre'
        ).annotate(
            total_ventas=Sum('total'),
            unidades_vendidas=Sum('cantidad')
        ).order_by('-total_ventas')
        
        categorias_list = []
        for cat in preferencias_categorias:
            categorias_list.append({
                "producto__categoria__nombre": cat['producto__categoria__nombre'],
                "total_ventas": float(cat['total_ventas'] or 0.0),
                "unidades_vendidas": int(cat['unidades_vendidas'] or 0)
            })

        # 5. ALGORITMO APRIORI NATIVO PARA ASOCIACIÓN DE PRODUCTOS
        # Umbrales ajustados para catálogos con variedad de productos.
        # Con muchos productos distintos, la probabilidad de que un par específico
        # supere el 3% es matemáticamente muy baja. 1% de soporte es suficiente
        # para detectar patrones reales sin requerir concentración artificial.
        reglas_asociacion = cls._calcular_apriori(min_support=0.01, min_confidence=0.15)

        return {
            "tasa_repeticion": round(tasa_repeticion, 2),
            "total_compradores": total_compradores,
            "compradores_recurrentes": compradores_recurrentes,
            "clientes": todos_clientes,
            "categorias": categorias_list,
            "reglas": reglas_asociacion
        }

    @classmethod
    def _calcular_apriori(cls, min_support=0.03, min_confidence=0.25):
        # Obtener transacciones (productos en una misma factura)
        from collections import defaultdict
        transacciones_dict = defaultdict(set)
        
        detalles = DetalleFactura.objects.filter(
            factura__estado='VIGENTE'
        ).select_related('producto')
        
        for det in detalles:
            transacciones_dict[det.factura_id].add(det.producto.nombre)
            
        transacciones = list(transacciones_dict.values())
        total_transacciones = len(transacciones)
        
        if total_transacciones == 0:
            return []

        # 1. Encontrar soporte de items individuales (C1)
        item_counts = defaultdict(int)
        for t in transacciones:
            for item in t:
                item_counts[item] += 1
                
        # Filtrar por soporte mínimo (L1)
        item_support = {}
        for item, count in item_counts.items():
            sup = count / total_transacciones
            if sup >= min_support:
                item_support[item] = sup
                
        frequent_items = list(item_support.keys())
        if len(frequent_items) < 2:
            return []

        # 2. Encontrar soporte de pares de items (C2)
        pair_counts = defaultdict(int)
        for t in transacciones:
            # Solo buscar combinaciones entre items frecuentes
            items_en_t = [x for x in t if x in item_support]
            for i in range(len(items_en_t)):
                for j in range(i + 1, len(items_en_t)):
                    pair = tuple(sorted([items_en_t[i], items_en_t[j]]))
                    pair_counts[pair] += 1

        # Generar reglas de asociación de pares (A -> B)
        reglas = []
        for pair, count in pair_counts.items():
            sup_conjunto = count / total_transacciones
            if sup_conjunto >= min_support:
                item_a, item_b = pair
                # Regla: A -> B
                conf_a_b = sup_conjunto / item_support[item_a]
                if conf_a_b >= min_confidence:
                    reglas.append({
                        "antecedente": item_a,
                        "consecuente": item_b,
                        "soporte": round(sup_conjunto * 100, 2),
                        "confianza": round(conf_a_b * 100, 2)
                    })
                # Regla: B -> A
                conf_b_a = sup_conjunto / item_support[item_b]
                if conf_b_a >= min_confidence:
                    reglas.append({
                        "antecedente": item_b,
                        "consecuente": item_a,
                        "soporte": round(sup_conjunto * 100, 2),
                        "confianza": round(conf_b_a * 100, 2)
                    })
                    
        # Ordenar reglas por confianza
        reglas = sorted(reglas, key=lambda x: x['confianza'], reverse=True)
        return reglas[:5] # Limitar a las 5 mejores reglas
