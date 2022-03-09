from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

from uuid import uuid4
from datetime import datetime, timedelta
from django.utils import timezone


def get_expire_time():
    expire_minutes = settings.EMAIL_AUTHORIZATION_EXPIRE
    return timezone.now() + timedelta(minutes=expire_minutes)


class User(AbstractUser):
    email = models.EmailField("Почтовый адрес", unique=True)


class EmailAuthorizationLetter(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    uuid = models.UUIDField(default=uuid4, editable=False)
    expire_on = models.DateTimeField(default=get_expire_time)
    created_at = models.DateTimeField(auto_now_add=True)
