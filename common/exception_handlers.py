from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.serializers import as_serializer_error
from rest_framework import exceptions


def exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    response = drf_exception_handler(exc, context)
    if isinstance(exc.detail, (list, dict)):
        response.data = {
            "detail": response.data
        }

    return response
