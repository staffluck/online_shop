from .models import User


def create_buyer_user(*, email: str) -> User:
    password = User.objects.make_random_password()
    user = User.objects.create_user(email=email, account_type=User.BUYER, password=password)
    return user
