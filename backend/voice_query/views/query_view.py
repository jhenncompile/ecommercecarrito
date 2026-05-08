from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services import VoiceQueryService
import logging

logger = logging.getLogger(__name__)

class VoiceQueryView(APIView):
    def post(self, request):
        print("!!! VOICE QUERY VIEW REACHED !!!")
        audio_file = request.FILES.get('audio')
        text_query = request.data.get('text') 

        if not audio_file and not text_query:
            return Response({"error": "No audio or text provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prompt = text_query
            if audio_file:
                prompt = VoiceQueryService.transcribe_audio(audio_file)
            
            if not prompt:
                return Response({"error": "Could not understand audio"}, status=status.HTTP_400_BAD_REQUEST)

            schema = VoiceQueryService.get_db_schema()
            sql = VoiceQueryService.generate_sql(prompt, schema)
            
            if not sql:
                return Response({
                    "prompt": prompt,
                    "error": "The AI could not generate a valid SELECT query for your request."
                }, status=status.HTTP_400_BAD_REQUEST)

            results = VoiceQueryService.execute_query(sql)

            return Response({
                "prompt": prompt,
                "sql": sql,
                "results": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in VoiceQueryView: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
