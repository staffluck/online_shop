from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS


User = get_user_model()


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsSeller(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return user.account_type == User.SELLER


class IsBuyer(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return user.account_type == User.Buyer


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
