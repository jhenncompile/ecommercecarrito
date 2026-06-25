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
        Only allowed tables are exposed to the AI to maintain security and tenant isolation.
        """
        from django.apps import apps
        from django.db import connection
        
        target_apps = ['app_negocio', 'customers']
        schema_description = []
        
        current_schema = getattr(connection, 'schema_name', 'unknown')
        schema_description.append(f"--- DATABASE DIALECT: PostgreSQL | CURRENT SCHEMA: {current_schema} ---")

        # Define strictly allowed tables for voice queries (avoiding cross-tenant data/admin leakage)
        allowed_tables = {
            'app_negocio_producto',
            'app_negocio_categoria',
            'app_negocio_carrito',
            'app_negocio_carrito_item',
            'app_negocio_pedido',
            'app_negocio_factura',
            'app_negocio_detalle_factura',
            'app_negocio_notificacion',
            'customers_cliente'  # Shared client customer table
        }

        for model in apps.get_models():
            table_name = model._meta.db_table
            if table_name not in allowed_tables:
                continue
                
            try:
                fields = []
                pk_field = model._meta.pk.name
                
                for field in model._meta.fields:
                    is_pk = field.name == pk_field
                    pk_indicator = " [PRIMARY KEY]" if is_pk else ""
                    
                    col_name = field.get_attname()
                    col_type = field.get_internal_type()
                    
                    if col_type == 'ForeignKey' or col_type == 'OneToOneField':
                        related_model = field.related_model._meta.db_table
                        related_pk = field.related_model._meta.pk.name
                        fields.append(f"{col_name} (FK -> {related_model}.{related_pk})")
                    else:
                        fields.append(f"{col_name} ({col_type}){pk_indicator}")
                
                schema_description.append(f"TABLE: {table_name}\nCOLUMNS: {', '.join(fields)}")
            except Exception as e:
                logger.warning(f"Could not load schema for model {model.__name__}: {str(e)}")
        
        return "\n\n".join(schema_description)

    @staticmethod
    def transcribe_audio(audio_input):
        """
        Transcribes audio using local Faster-Whisper.
        audio_input can be a Django UploadedFile or a string file path.
        """
        try:
            model = get_whisper_model()

            is_path = isinstance(audio_input, str)
            if is_path:
                tmp_path = audio_input
            else:
                # Save uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                    for chunk in audio_input.chunks():
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
            # Si creamos un archivo temporal nuevo, lo borramos. Si era un path pasado, el caller se encarga de borrarlo si quiere.
            if not is_path and 'tmp_path' in locals() and os.path.exists(tmp_path):
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
            raise Exception("ConfiguraciÃ³n de IA incompleta (Falta API Key).")

        system_prompt = f"""
        You are a precise PostgreSQL SQL generator. Convert the user's natural language request into a valid SQL query.
        
        ### SCHEMA RULES:
        {schema}
        
        ### SECURITY & TENANT ISOLATION RULES (CRITICAL):
        1. You are operating in a multi-tenant environment. The active tenant schema is '{connection.schema_name}'.
        2. You must ONLY generate SELECT queries targeting the allowed tables described in the schema above.
        3. Never attempt to query, join, or reference any other tables not explicitly listed in the schema above (e.g., customers_usuario, customers_client, django_session, auth_group, etc.).
        4. Do NOT use schema prefixes (e.g., use 'app_negocio_producto', NOT '{connection.schema_name}.app_negocio_producto').
        5. PostgreSQL automatically routes tenant-specific queries to the correct schema. Your generated SQL must operate securely within these boundaries.
        
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
11. SORTING (ORDER BY): NEVER return an unordered result set. Every query MUST have an ORDER BY clause. For reports, default to ordering by date descending, then by primary key descending. NEVER use '.id' unless 'id' is explicitly a column in the table. For 'app_negocio_factura', order by f.fecha DESC, f.nro DESC — NOT f.fecha_creacion.
12. DATES & TIME: For "this month", strictly use: date_column >= DATE_TRUNC('month', CURRENT_DATE) AND date_column < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'. For formatting outputs, use TO_CHAR(date_column, 'YYYY-MM-DD') to ensure consistent reading.
16. EXACT COLUMN NAMES PER TABLE (CRITICAL — never invent column names):
    - app_negocio_factura: nro [PK], fecha (DateField), hora (TimeField), pedido_id (FK->app_negocio_pedido.id), cliente_id, tipo_pago_id, monto_total, moneda, cuf, estado. THERE IS NO 'fecha_creacion' column.
    - app_negocio_pedido: id [PK], carrito_id (FK->app_negocio_carrito.id), estado, tracking_code.
    - app_negocio_producto: id [PK], nombre, descripcion, precio, costo, stock, categoria_id, activo.
    - app_negocio_detalle_factura: id [PK], factura_id (FK->app_negocio_factura.nro), producto_id, cantidad, precio_unitario, total.
    - app_negocio_categoria: id [PK], nombre, descripcion, fecha_creacion.
    - customers_cliente: id [PK], nombre, apellido, email, telefono, fecha_creacion.
13. SMART ANALYTICS: When requested for top items, rankings, or performance over time, utilize Window Functions (RANK(), SUM() OVER()) to provide deep insights without losing row-level context.
14. MULTI-TENANCY: Do not use schema prefixes. Just use the exact table names provided in the schema (e.g. use 'customers_cliente', NEVER invent 'app_negocio_cliente').
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
        
        # Models to try if the primary one is rate-limited
        fallback_models = [
            model,
            "meta-llama/llama-3.3-70b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "nousresearch/hermes-3-llama-3.1-405b:free"
        ]
        
        response = None
        used_model = None
        
        for current_model in fallback_models:
            data = {
                "model": current_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User Request: {prompt}"}
                ],
                "temperature": 0.1
            }
            
            try:
                resp = requests.post(url, headers=headers, json=data, timeout=30)
                if resp.status_code == 200:
                    response = resp
                    used_model = current_model
                    break
                else:
                    logger.warning(f"Model {current_model} falló ({resp.status_code}): {resp.text}. Intentando con el siguiente fallback...")
                    continue
            except requests.exceptions.RequestException as e:
                logger.warning(f"Connection Error with {current_model}: {str(e)}")
                continue

        if not response:
            raise Exception("Todos los modelos de IA están rate-limited o caídos. Intenta de nuevo más tarde.")
        
        try:
            content = response.json()['choices'][0]['message']['content'].strip()
            logger.info(f"Generated successfully using model: {used_model}")
            
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
        except KeyError as e:
            logger.error(f"Error parsing AI response from {used_model}: {str(e)}")
            raise Exception("No se pudo procesar la respuesta de la IA.")

    @staticmethod
    def _serialize_row(row: dict) -> dict:
        """
        Converts non-JSON-serializable types (date, datetime, Decimal, UUID, etc.)
        to their string equivalents so results can be stored in a JSONField.
        """
        import datetime
        from decimal import Decimal
        import uuid

        serialized = {}
        for key, value in row.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                serialized[key] = value.isoformat()
            elif isinstance(value, datetime.time):
                serialized[key] = value.isoformat()
            elif isinstance(value, Decimal):
                serialized[key] = float(value)
            elif isinstance(value, uuid.UUID):
                serialized[key] = str(value)
            elif isinstance(value, memoryview):
                serialized[key] = bytes(value).hex()
            else:
                serialized[key] = value
        return serialized

    @staticmethod
    def execute_query(sql):
        """
        Executes the SQL query and returns the result as a list of dictionaries.
        All values are JSON-serializable (dates → ISO strings, Decimal → float, etc.)
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
                    VoiceQueryService._serialize_row(dict(zip(columns, row)))
                    for row in cursor.fetchall()
                ]
                logger.info(f"Query executed successfully. Rows returned: {len(results)}")
                return results
        except Exception as e:
            logger.error(f"Database Execution Error: {str(e)}\nSQL: {sql}")
            raise Exception(f"Error al ejecutar la consulta en la base de datos: {str(e)}")

    @staticmethod
    def run_async_voice_task(task_id, schema, text_query, audio_path):
        from django_tenants.utils import schema_context
        from apps.voice.models import VoiceTask
        
        with schema_context(schema):
            try:
                task = VoiceTask.objects.get(id=task_id)
                task.status = 'PROCESSING'
                task.save(update_fields=['status'])
                
                prompt = text_query
                if audio_path:
                    logger.info(f"Task {task_id}: Processing audio file: {audio_path}")
                    prompt = VoiceQueryService.transcribe_audio(audio_path)
                    
                    # Cleanup audio file after processing
                    try:
                        if os.path.exists(audio_path):
                            os.remove(audio_path)
                    except Exception as e:
                        logger.warning(f"Task {task_id}: Could not delete temporary audio file {audio_path}: {e}")

                if not prompt:
                    task.status = 'FAILURE'
                    task.error_message = "No pude entender lo que dijiste. Intenta de nuevo."
                    task.save(update_fields=['status', 'error_message'])
                    return

                task.prompt = prompt
                task.save(update_fields=['prompt'])
                logger.info(f"Task {task_id}: Prompt understood: {prompt}")
                
                schema_desc = VoiceQueryService.get_db_schema()
                sql = VoiceQueryService.generate_sql(prompt, schema_desc)
                task.sql_query = sql
                task.save(update_fields=['sql_query'])
                
                upper_sql = sql.upper().strip()
                if not (upper_sql.startswith('SELECT') or upper_sql.startswith('WITH')):
                    task.status = 'FAILURE'
                    task.error_message = sql if sql else "La IA no pudo generar una consulta SQL válida para tu petición."
                    task.save(update_fields=['status', 'error_message'])
                    return

                results = VoiceQueryService.execute_query(sql)
                
                task.results = results
                task.status = 'SUCCESS'
                task.save(update_fields=['results', 'status'])
                logger.info(f"Task {task_id}: Processing completed successfully.")

            except Exception as e:
                logger.exception(f"Task {task_id}: Error processing voice query")
                try:
                    task = VoiceTask.objects.get(id=task_id)
                    task.status = 'FAILURE'
                    task.error_message = str(e)
                    task.save(update_fields=['status', 'error_message'])
                except Exception:
                    pass



