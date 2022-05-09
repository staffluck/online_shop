from typing import Any, Union, Tuple, List

from django.utils import timezone

from common.mail import send_mail
from .models import EmailAuthorizationLetter, User


def create_buyer_user(*, email: str) -> User:
    password = User.objects.make_random_password()
    user = User.objects.create_user(email=email, account_type=User.AccountTypes.BUYER, password=password)
    return user


class EmailAuthorizationLetterSendService:

    def __init__(self, *, user: User, to_email: str, auth_url: str):
        self.user = user
        self.subject = "Authrorization letter from online_shop"
        self.message = "{}".format(auth_url+"{}/")
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
        self.message = self.message.format(letter.uuid)
        return letter

    def send_auth_email_letter(self) -> Any:
        return send_mail.delay([self.to_email, ], self.subject, self.message)


class EmailAuthorizationLetterProccessingService:

    def __init__(self, *, letter_uuid: str):
        self.letter_uuid = letter_uuid

    def execute(self) -> Union[bool, User]:
        is_exist, letter = self.get_letter()

        if is_exist:
            letter.delete()
        if not is_exist or letter.expire_on < timezone.now():
            return False

        return letter.user

    def get_letter(self) -> Union[Tuple[bool, List], Tuple[bool, EmailAuthorizationLetter]]:
        letter = EmailAuthorizationLetter.objects.select_related("user").filter(uuid=self.letter_uuid)
        if letter.exists():
            return (True, letter.first())
        return (False, [])
