from rest_framework import serializers
from api.models.user_models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Profile
        fields = ['id', 'user_username', 'gender', 'birth_date']
        read_only_fields = ['user_username',]

