from rest_framework import serializers
from .models import User

from djoser.serializers import UserSerializer as djoser_UserSerializer
from djoser.serializers import UserCreateSerializer as djoser_UserCreateSerializer

class UserSerializer(djoser_UserSerializer):

    class Meta:
        model = User
        fields = ['username', "email", "first_name", "last_name"]
        ref_name = "User 1"

class UserCreateSerializer(djoser_UserCreateSerializer):

    def perform_create(self, validated_data):
        validated_data["username"] = validated_data["email"]
        return super().perform_create(validated_data)

class EmailAuthenticationLetterSendSerializer(serializers.Serializer):
    email = serializers.EmailField()
