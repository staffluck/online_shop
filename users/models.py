from uuid import uuid4
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


def get_expire_time():
    expire_minutes = settings.EMAIL_AUTHORIZATION_EXPIRE
    return timezone.now() + timedelta(minutes=expire_minutes)


class User(AbstractUser):
    BUYER = 0
    SELLER = 1
    ACCOUNT_TYPES = (
        (BUYER, "Buyer"),
        (SELLER, "Seller"),
    )
    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS + ["account_type"]

    account_type = models.IntegerField(default=1, choices=ACCOUNT_TYPES)
    email = models.EmailField("Почтовый адрес", unique=True)


class EmailAuthorizationLetter(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    uuid = models.UUIDField(default=uuid4, editable=False)
    expire_on = models.DateTimeField(default=get_expire_time)
    created_at = models.DateTimeField(auto_now_add=True)
