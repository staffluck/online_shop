from .models import User
from .services import create_buyer_user


def get_or_create_buyer_user(*, email: str) -> User:
    user = User.objects.filter(email=email)
    if not user.exists():
        user = create_buyer_user(email=email)
    else:
        user = user.first()

    return user
