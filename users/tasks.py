from smtplib import SMTPException
from typing import Union

from celery.exceptions import Ignore
from celery import shared_task
from django.core.mail import send_mail as django_send_mail
from django.conf import settings

@shared_task(name="send_mail")
def send_mail(send_to: Union[tuple, list], subject: str, message: str) -> None:
    from_email = settings.EMAIL_HOST_USER
    django_send_mail(subject, message, from_email, send_to)
