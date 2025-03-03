import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.models.transcription_models import Transcription
from api.serializers.transcription_serializers import TranscriptionSerializer
from django.conf import settings


class TranscriptionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        audio_file = request.FILES.get('audio_file')
        name = request.data.get('name')
        folder = request.data.get('folder')

        if not audio_file or not name:
            return Response({'error': 'Fichier audio et nom requis'}, status=status.HTTP_400_BAD_REQUEST)

        transcription = Transcription.objects.create(
            user=request.user,
            name=name,
            audio_file=audio_file,
            folder=folder
        )

        # 1️⃣ Transcription avec Whisper API
        try:
            whisper_response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers={'Authorization': f'Bearer {settings.OPENAI_API_KEY}'},
                files={'file': (audio_file.name, audio_file, 'audio/mpeg')},
                data={'model': 'whisper-1', 'language': 'fr'}
            )
            whisper_result = whisper_response.json()
            content_raw = whisper_result.get('text')

            if not content_raw:
                return Response({'error': 'Échec de la transcription Whisper', 'details': whisper_result}, status=500)

            transcription.content_raw = content_raw
            transcription.save()

        except Exception as e:
            return Response({'error': f'Erreur Whisper : {str(e)}'}, status=500)

        try:
            llama_response = requests.post(
                'https://gtp.charlesago.com/api/chat',
                json={
                    'messages': [
                        {'role': 'system', 'content': 'Tu es un assistant qui reformule proprement des cours.'},
                        {'role': 'user', 'content': f"Corrige et reformule ce texte : {content_raw}"}
                    ],
                    'stream': False
                }
            )

            llama_result = llama_response.json()
            content_cleaned = llama_result.get('message', {}).get('content', '')

            transcription.content_cleaned = content_cleaned
            transcription.save()

        except Exception as e:
            return Response({'error': f'Erreur Llama : {str(e)}'}, status=500)

        serializer = TranscriptionSerializer(transcription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
