from rest_framework import serializers
from .models import User

from djoser.serializers import UserSerializer as djoser_UserSerializer

class UserSerializer(djoser_UserSerializer):

    class Meta:
        model = User
        fields = ['username', "email", "first_name", "last_name"]
        ref_name = "User 1"

class EmailAuthenticationLetterSendSerializer(serializers.Serializer):
    email = serializers.EmailField()
