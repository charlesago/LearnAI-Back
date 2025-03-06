from rest_framework import serializers
from api.models.folder_models import UserFolder
from api.models.folder_models import UserFile

class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = '__all__'

class UserFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFolder
        fields = '__all__'
