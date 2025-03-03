from rest_framework import serializers
from api.models.transcription_models import Transcription


class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcription
        fields = '__all__'
        read_only_fields = ['user', 'content_raw', 'content_cleaned', 'created_at']
