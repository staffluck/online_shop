import django_filters
from rest_framework.request import Request
from django.db.models import QuerySet

from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    mine = django_filters.BooleanFilter(method="get_mine_filter")

    class Meta:
        model = Product
        fields = ["name", "mine"]

    def get_mine_filter(self, queryset, mine, value):
        if value:
            return queryset.filter(owner=self.request.user)
        else:
            return queryset.exclude(owner=self.request.user)

def get_products_list(*, request: Request, queryset: QuerySet, filters: dict = None):
    if not filters:
        filters = {}
    if not queryset:
        queryset = Product.objects.all()

    return ProductFilter(filters, queryset, request=request).qs
