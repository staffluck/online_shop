from rest_framework.pagination import BasePagination
from rest_framework.serializers import BaseSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import QuerySet
from django.views.generic import View


def get_paginated_response(*, pagination_class: BasePagination, serializer_class: BaseSerializer, queryset: QuerySet, request: Request, view: View) -> Response:
    paginator = pagination_class()
    page = paginator.paginate_queryset(queryset, request, view=view)
    serializer = serializer_class(page if page else queryset, many=True)

    return paginator.get_paginated_response(serializer.data)
