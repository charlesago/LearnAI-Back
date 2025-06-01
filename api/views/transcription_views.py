import requests
import json
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from api.models.transcription_models import Transcription
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

@csrf_exempt
def upload_form(request):
    return render(request, '../templates/transcriptions/upload.html')

WHISPER_URL = "https://whisper.charlesago.com/transcribe/"
IA_URL = "https://openai.charlesago.com/api/chat/completions"
IA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk3YTA4ZTc2LTNlYWItNDgwZC1iYzMzLTRhYzczMDgyMDI0OCJ9.SBVZCMh0n0ErlkZFQA4__Y7BJPx_vJNVp4MGmq5oiEQ"

@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([AllowAny])
def upload_and_transcribe(request):
    audio_file = request.FILES['audio']
    folder = request.POST.get("folder", "")

    # Étape 1 : appel Whisper
    whisper_response = requests.post(WHISPER_URL, files={'file': audio_file})
    if whisper_response.status_code != 200:
        return JsonResponse({'error': 'Whisper API failed'}, status=500)

    transcription_text = whisper_response.json().get("transcription", "")

    # Étape 2 : appel IA avec stream
    headers = {
        "Authorization": f"Bearer {IA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3.2:3b",  # pas "mistral:7b" pour OpenAI compatible
        "messages": [
            {"role": "user", "content": f"Fais-moi un résumé de ce texte :\n\n{transcription_text}"}
        ],
        "stream": True
    }

    try:
        response = requests.post(IA_URL, headers=headers, json=payload, stream=True, timeout=120)
        if response.status_code != 200:
            return JsonResponse({
                "error": "AI summary failed",
                "status": response.status_code,
                "raw": response.text
            }, status=500)

        summary = ""
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                content = line.removeprefix("data: ").strip()
                if content == "[DONE]":
                    break
                try:
                    chunk = json.loads(content)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    summary += delta.get("content", "")
                except Exception:
                    continue

    except Exception as e:
        return JsonResponse({
            "error": "Exception during stream",
            "details": str(e)
        }, status=500)

    # Étape 3 : enregistrement en BDD
    transcription = Transcription.objects.create(
        name=audio_file.name,
        audio_file=audio_file,
        content_raw=transcription_text,
        content_cleaned=summary,
        folder=folder,
    )

    return JsonResponse({
        "id": transcription.id,
        "summary": summary
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_summary(request, transcription_id):
    try:
        t = Transcription.objects.get(id=transcription_id)
    except Transcription.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    return JsonResponse({
        "summary": t.content_cleaned,
        "status": "done" if t.content_cleaned else "processing"
    })
