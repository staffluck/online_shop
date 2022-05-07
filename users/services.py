from typing import Tuple, Any

from common.mail import send_mail
from .models import EmailAuthorizationLetter, User


def create_buyer_user(*, email: str) -> User:
    password = User.objects.make_random_password()
    user = User.objects.create_user(email=email, account_type=User.BUYER, password=password)
    return user


class EmailAuthorizationLetterProcessingService:

    def __init__(self, *, user: User, to_email: str, auth_url: str):
        self.user = user
        self.subject = "Authrorization letter from online_shop"
        self.message = "{}".format(auth_url)
        self.to_email = to_email

    def execute(self) -> Tuple[EmailAuthorizationLetter, Any]:
        _ = self.delete_email_letter()
        letter = self.create_auth_email_letter()
        task_info = self.send_auth_email_letter()
        return letter, task_info

    def delete_email_letter(self) -> tuple:
        current_letter = EmailAuthorizationLetter.objects.filter(user=self.user)
        return current_letter.delete()

    def create_auth_email_letter(self) -> EmailAuthorizationLetter:
        letter = EmailAuthorizationLetter.objects.create(user=self.user)
        self.message.format(letter.uuid)
        return letter

    def send_auth_email_letter(self):
        return send_mail.delay([self._to_email, ], self.subject, self.message)
