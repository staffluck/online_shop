#  Модуль для определния сервисов/селекторов, которые используют другие сервисы/селекторы, дабы избежать цикличного импорта.

from users.models import User
from users.services import create_buyer_user


def get_or_create_buyer_user(*, email: str) -> User:
    user = User.objects.filter(email=email)
    if not user.exists():
        user = create_buyer_user(email=email)
    else:
        user = user.first()

    return user
