import os
import requests
import json
from django.db import connection
from decouple import config
import tempfile
import logging

logger = logging.getLogger(__name__)

# Caching the model to avoid reloading on every request
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        model_size = config('WHISPER_MODEL_SIZE', default='base')
        logger.info(f"Loading local Whisper model: {model_size}")
        # device="cpu" and compute_type="int8" is good for most servers without GPU
        _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _whisper_model

class VoiceQueryService:
    @staticmethod
    def get_db_schema():
        """
        Extracts the schema of the current tenant's tables and relevant shared tables.
        """
        from django.apps import apps
        from django.db import connection
        
        # We include both app_negocio (tenant-specific data) and customers (client/user data)
        target_apps = ['app_negocio', 'customers']
        schema_description = []
        
        current_schema = getattr(connection, 'schema_name', 'unknown')
        schema_description.append(f"--- DATABASE DIALECT: PostgreSQL | CURRENT SCHEMA: {current_schema} ---")

        for app_label in target_apps:
            try:
                app_config = apps.get_app_config(app_label)
                app_models = app_config.get_models()
                
                for model in app_models:
                    table_name = model._meta.db_table
                    fields = []
                    pk_field = model._meta.pk.name
                    
                    for field in model._meta.fields:
                        is_pk = field.name == pk_field
                        pk_indicator = " [PRIMARY KEY]" if is_pk else ""
                        
                        # Get actual DB column name
                        col_name = field.get_attname()
                        col_type = field.get_internal_type()
                        
                        if col_type == 'ForeignKey' or col_type == 'OneToOneField':
                            # For FKs, explain what they point to
                            related_model = field.related_model._meta.db_table
                            related_pk = field.related_model._meta.pk.name
                            fields.append(f"{col_name} (FK -> {related_model}.{related_pk})")
                        else:
                            fields.append(f"{col_name} ({col_type}){pk_indicator}")
                    
                    schema_description.append(f"TABLE: {table_name}\nCOLUMNS: {', '.join(fields)}")
            except Exception as e:
                logger.warning(f"Could not load schema for app {app_label}: {str(e)}")
        
        return "\n\n".join(schema_description)

    @staticmethod
    def transcribe_audio(audio_file):
        """
        Transcribes audio using local Faster-Whisper.
        """
        try:
            model = get_whisper_model()

            # Save uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                for chunk in audio_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            logger.info(f"Transcribing audio file: {tmp_path}")
            segments, info = model.transcribe(tmp_path, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            transcription = text.strip()
            logger.info(f"Transcription result: {transcription}")
            return transcription
        except Exception as e:
            logger.error(f"Local Whisper Error: {str(e)}")
            # Fallback a un error más amigable si no hay ffmpeg
            if "ffmpeg" in str(e).lower():
                raise Exception("El sistema de transcripción requiere FFmpeg. Por favor, instálalo en el servidor.")
            raise Exception(f"Error en la transcripción local: {str(e)}")
        finally:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

    @staticmethod
    def generate_sql(prompt, schema):
        """
        Generates an optimal SQL query using OpenRouter.
        """
        api_key = config('OPENROUTER_API_KEY', default=None)
        model = config('OPENROUTER_MODEL', default='openai/gpt-3.5-turbo')
        
        if not api_key:
            logger.error("OPENROUTER_API_KEY not found in configuration")
            raise Exception("Configuración de IA incompleta (Falta API Key).")

        system_prompt = f"""
        You are a precise PostgreSQL SQL generator. Convert the user's natural language request into a valid SQL query.
        
        ### SCHEMA RULES:
        {schema}
        
        ### CRITICAL INSTRUCTIONS (ENHANCED):

1. PRIMARY KEYS: Look for [PRIMARY KEY] markers. NEVER assume a table has an 'id' column unless it is explicitly listed. For example, 'app_negocio_factura' uses 'nro' as PK.
2. JOINS: Use the exact column names for joins. If a column is listed as factura_id (FK -> app_negocio_factura.nro), you must join using app_negocio_factura.nro = table.factura_id.
3. OUTPUT: Return ONLY the raw SQL query. No markdown code blocks (```sql), no comments, no explanations, no preamble. Just the raw string executable by the database.
4. DIALECT: Use PostgreSQL. Use ILIKE for case-insensitive text matching.
5. NULL HANDLING (CRITICAL): ALWAYS use COALESCE() for columns involved in mathematical operations or string concatenations to prevent returning NULL. Example: COALESCE(p.costo, 0).
6. SOFT DELETES & STATUS: NEVER include deleted, cancelled, or inactive records in reports unless explicitly requested. Always filter using available status columns (e.g., WHERE estado != 'anulado', WHERE is_active = true, or WHERE deleted_at IS NULL).
7. DETAIL OVER AGGREGATION: Unless the user specifically asks for "just the total", ALWAYS favor returning a detailed list of records with context. Include dates, names, categories, and individual totals alongside window functions for running totals if appropriate.
8. RELEVANT COLUMNS: Always include descriptive columns like names, categories, and dates to give context to the numbers. Join with customers_cliente, app_negocio_categoria, or similar tables to show human-readable names instead of raw IDs.
9. SCALAR COMPARISONS: Use LEAST(a, b) instead of MIN(a, b) and GREATEST(a, b) instead of MAX(a, b) for comparing two values on the same row. MIN/MAX are ONLY for aggregate functions.
10. BUSINESS LOGIC & METRICS
    - 'Ganancia Potencial' = (COALESCE(p.precio, 0) - COALESCE(p.costo, 0)) * COALESCE(p.stock, 0).
    - 'Ventas Totales' = Must list details of sales first, then the sum.
    - 'Rentabilidad' = ((p.precio - p.costo) / NULLIF(p.precio, 0)) * 100. Round this to 2 decimal places using ROUND(..., 2).
11. SORTING (ORDER BY): NEVER return an unordered result set. Every query MUST have an ORDER BY clause. For reports, default to ordering by date descending (fecha DESC), then by primary key descending.
12. DATES & TIME: For "this month", strictly use: date_column >= DATE_TRUNC('month', CURRENT_DATE) AND date_column < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'. For formatting outputs, use TO_CHAR(date_column, 'YYYY-MM-DD HH24:MI') to ensure consistent reading.
13. SMART ANALYTICS: When requested for top items, rankings, or performance over time, utilize Window Functions (RANK(), SUM() OVER()) to provide deep insights without losing row-level context.
14. MULTI-TENANCY: Do not use schema prefixes. Just use the table names.
15. SECURITY: Only SELECT queries are allowed. Never generate INSERT, UPDATE, DELETE, DROP, or ALTER.
        """
        
        logger.info(f"--- VOICE QUERY PROMPT ---\n{prompt}\n--------------------------")
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Ecommerce Voice Assistant"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Request: {prompt}"}
            ],
            "temperature": 0.1
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code != 200:
                logger.error(f"OpenRouter Error {response.status_code}: {response.text}")
                raise Exception(f"Error del servicio de IA: {response.status_code}")
            
            content = response.json()['choices'][0]['message']['content'].strip()
            
            # Clean up AI response
            sql = content
            if '```' in sql:
                import re
                # Extract content inside markdown if present, else just strip markdown tags
                match = re.search(r'```(?:sql)?\n?(.*?)\n?```', sql, re.DOTALL | re.IGNORECASE)
                if match:
                    sql = match.group(1).strip()
                else:
                    sql = re.sub(r'```sql\n?|```', '', sql).strip()
            
            # Remove trailing semicolon if present
            if sql.endswith(';'):
                sql = sql[:-1].strip()

            # Fix common "SELECTsomething" typo
            if sql.upper().startswith('SELECT') and not sql.upper().startswith('SELECT '):
                sql = 'SELECT ' + sql[6:]

            logger.info(f"--- GENERATED SQL ---\n{sql}\n----------------------")
            
            # Final validation
            upper_sql = sql.upper()
            if not (upper_sql.startswith('SELECT') or upper_sql.startswith('WITH')):
                logger.warning(f"AI generated non-SQL response: {sql}")
                # Return the explanation as is, the view will handle it
                return sql

            forbidden = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE']
            for word in forbidden:
                import re
                if re.search(rf'\b{word}\b', upper_sql):
                    logger.warning(f"Security violation: {word}")
                    raise Exception(f"Comando prohibido detectado: {word}")
            
            return sql
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter Connection Error: {str(e)}")
            raise Exception("No se pudo conectar con el servicio de IA.")

    @staticmethod
    def execute_query(sql):
        """
        Executes the SQL query and returns the result as a list of dictionaries.
        """
        from django.db import connection
        if not sql:
            return []

        try:
            with connection.cursor() as cursor:
                logger.info(f"Executing SQL: {sql}")
                cursor.execute(sql)
                
                if cursor.description is None:
                    return []
                    
                columns = [col[0] for col in cursor.description]
                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
                logger.info(f"Query executed successfully. Rows returned: {len(results)}")
                return results
        except Exception as e:
            logger.error(f"Database Execution Error: {str(e)}\nSQL: {sql}")
            raise Exception(f"Error al ejecutar la consulta en la base de datos: {str(e)}")

