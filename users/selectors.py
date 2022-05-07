from typing import Union, Tuple, List, Optional

from .models import User


def get_user_by_id(*, id: int) -> Union[Tuple[bool, List], Tuple[bool, User]]:
    user = User.objects.filter(id=id)
    if user.exists():
        return (True, user.first())
    return (False, [])


def get_user(*, email: Optional[str] = None, username: Optional[str] = None) -> Union[Tuple[bool, List], Tuple[bool, User]]:
    query_filters = {}
    if email:
        query_filters["email"] = email
    if username:
        query_filters["username"] = username
    user = User.objects.filter(**query_filters)

    if query_filters and user.exists():
        return (True, user.first())
    return (False, [])
