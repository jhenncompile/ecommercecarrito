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
        Extracts the schema of the current tenant's tables.
        We focus on app_negocio models.
        """
        from django.apps import apps
        app_models = apps.get_app_config('app_negocio').get_models()
        
        schema_description = []
        for model in app_models:
            table_name = model._meta.db_table
            fields = []
            pk_field = model._meta.pk.name
            
            for field in model._meta.fields:
                pk_indicator = " (PRIMARY KEY)" if field.name == pk_field else ""
                # Use get_attname() to get the actual column name (e.g. tipo_pago_id instead of tipo_pago)
                fields.append(f"{field.get_attname()} ({field.get_internal_type()}){pk_indicator}")
            
            schema_description.append(f"Table: {table_name}\nFields: {', '.join(fields)}")
        
        return "\n\n".join(schema_description)

    @staticmethod
    def transcribe_audio(audio_file):
        """
        Transcribes audio using local Faster-Whisper.
        """
        model = get_whisper_model()

        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            segments, info = model.transcribe(tmp_path, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            logger.error(f"Local Whisper Error: {str(e)}")
            raise Exception(f"Error en la transcripción local: {str(e)}")
        finally:
            if os.path.exists(tmp_path):
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
            raise Exception("OPENROUTER_API_KEY not found in .env")

        system_prompt = f"""
        You are an expert SQL analyst for PostgreSQL. Generate a valid query based on the user's request and the EXACT schema below.
        
        STRICT RULES:
        1. ONLY output the SQL query. No markdown, no comments, no explanations.
        2. ONLY use SELECT queries.
        3. CRITICAL: Use the EXACT column names provided in the schema below. 
        4. NOTE: ForeignKey fields usually end in '_id' (e.g., 'tipo_pago_id'). Use these for JOINs.
        5. CRITICAL: Pay attention to (PRIMARY KEY) markers. For 'app_negocio_factura', the primary key is 'nro'.
        6. Always ensure a space after 'SELECT'.
        7. NEVER use a column alias defined in the SELECT list for another calculation in the same SELECT list. You MUST repeat the full expression. Example: instead of '(alias * 2)', use '((original_col * factor) * 2)'.
        8. If you cannot fulfill the request, return an empty string.
        
        SCHEMA:
        {schema}
        """
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000", # Optional
            "X-Title": "Ecommerce Voice Query" # Optional
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Request: {prompt}"}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"OpenRouter Error: {response.text}")
        
        sql = response.json()['choices'][0]['message']['content'].strip()
        
        # Post-processing to fix common AI typos
        if sql.upper().startswith('SELECT') and not sql.upper().startswith('SELECT '):
            sql = 'SELECT ' + sql[6:]
        
        # Remove any leading/trailing markdown code blocks if the AI ignored the rule
        if sql.startswith('```'):
            import re
            sql = re.sub(r'```sql\n?|```', '', sql).strip()

        print(f"--- GENERATED SQL ---\n{sql}\n---------------------")
        # Basic security check
        forbidden = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE']
        upper_sql = sql.upper()
        for word in forbidden:
            if word in upper_sql:
                import re
                if re.search(rf'\b{word}\b', upper_sql):
                    raise Exception(f"Security Violation: Forbidden keyword '{word}' detected in generated SQL.")
        
        if not upper_sql.startswith('SELECT') and not upper_sql.startswith('WITH'):
             raise Exception("Security Violation: Only SELECT queries are allowed.")

        return sql

    @staticmethod
    def execute_query(sql):
        """
        Executes the SQL query and returns the result as a list of dictionaries.
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
