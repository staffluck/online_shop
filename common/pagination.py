from rest_framework.pagination import BasePagination
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import inline_serializer
from django.db.models import QuerySet
from django.views.generic import View


def get_paginated_response(*, pagination_class: BasePagination, serializer_class: serializers.BaseSerializer, queryset: QuerySet, request: Request, view: View) -> Response:
    paginator = pagination_class()
    page = paginator.paginate_queryset(queryset, request, view=view)
    serializer = serializer_class(page if page else queryset, many=True)

    return paginator.get_paginated_response(serializer.data)

def get_paginated_response_schema(nested_serializer: serializers.BaseSerializer):
    response_schema = inline_serializer(
        name="ProductPaginatedSerializer",
        fields={
            "count": serializers.IntegerField(),
            "next": serializers.URLField(),
            "previous": serializers.URLField(),
            "results": nested_serializer(many=True)
        }
    )
    return response_schema
