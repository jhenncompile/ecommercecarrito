from django.core.cache import cache
from django.db import connection
from ..models.producto import Producto

class RecommendationService:
    # Lista explícita de stop words en español (Evita el error de scikit-learn)
    STOP_WORDS_ES = [
        'un', 'una', 'unas', 'unos', 'el', 'la', 'las', 'lo', 'los', 'al', 'del',
        'y', 'e', 'o', 'u', 'en', 'de', 'a', 'que', 'es', 'con', 'para', 'por',
        'su', 'sus', 'esta', 'este', 'estos', 'estas', 'pero', 'mas', 'muy'
    ]

    def obtener_recomendaciones(self, producto_id, top_n=3):
        # 1. Intentar obtener de caché (Tenant-Safe)
        # connection.schema_name es la propiedad usada en este proyecto
        schema = connection.schema_name
        cache_key = f"reco_{schema}_{producto_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        # Lazy import de dependencias pesadas para no romper el arranque del servidor
        try:
            import pandas as pd
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except Exception as e:
            # Proveer mensaje claro si faltan paquetes
            raise ImportError(
                "Faltan dependencias requeridas para recommendations (pandas, scikit-learn). "
                "Instala con: pip install pandas scikit-learn"
            ) from e

        # 2. Obtener solo productos activos (Aislamiento de negocio)
        productos = Producto.objects.filter(activo=True).select_related('categoria')
        if not productos.exists():
            return []

        # 3. Procesamiento seguro de datos
        df = pd.DataFrame(list(productos.values('id', 'nombre', 'descripcion', 'categoria__nombre')))
        df['nombre'] = df['nombre'].fillna('')
        df['descripcion'] = df['descripcion'].fillna('')
        df['categoria__nombre'] = df['categoria__nombre'].fillna('')

        df['metadata'] = df['nombre'] + " " + df['descripcion'] + " " + df['categoria__nombre']

        # 4. TF-IDF con normalización unicode para e-commerce
        tfidf = TfidfVectorizer(
            stop_words=self.STOP_WORDS_ES,
            strip_accents='unicode',
            lowercase=True,
            ngram_range=(1, 2) 
        )
        tfidf_matrix = tfidf.fit_transform(df['metadata'])
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        try:
            idx = df[df['id'] == producto_id].index[0]
        except IndexError:
            return []

        # 5. Ranking y Score
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]

        # Guardamos el ID y el Score para preservar la relevancia
        resultados = [(df['id'].iloc[i], score) for i, score in sim_scores]

        # Guardar en caché por 1 hora para no matar el CPU
        cache.set(cache_key, resultados, 3600)
        return resultados