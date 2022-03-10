from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', "email", "first_name", "last_name"]
        ref_name = "User 1"

class EmailAuthenticationLetterSendSerializer(serializers.Serializer):
    email = serializers.EmailField()
