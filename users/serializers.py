from rest_framework import serializers
from .models import User

from djoser.serializers import UserSerializer as djoser_UserSerializer, UserCreateSerializer as djoser_UserCreateSerializer


class UserSerializer(djoser_UserSerializer):

    class Meta:
        model = User
        fields = ['username', "email", "first_name", "last_name"]
        ref_name = "User 1"


class UserCreateSerializer(djoser_UserCreateSerializer):
    pass


class EmailAuthenticationLetterSendInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
