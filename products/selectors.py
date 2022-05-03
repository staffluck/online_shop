from typing import List, Optional, Tuple, Union
from random import choice
import django

import django_filters
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from django.db.models import QuerySet

from users.models import User
from .models import Deal, Product, ProductItem


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

class DealFilter(django_filters.FilterSet):

    class Meta:
        model = Deal
        fields = ["status", ]


def get_products_list(*, request: Request, queryset: Optional[QuerySet] = None, filters: Optional[dict] = None) -> QuerySet[Product]:
    if not filters:
        filters = {}
    if queryset is None:
        queryset = Product.objects.all()

    return ProductFilter(filters, queryset, request=request).qs

def get_product_by_id(*, id: int, queryset: Optional[QuerySet] = None) -> Union[Tuple[bool, List], Tuple[bool, Product]]:
    if queryset is None:
        queryset = Product.objects.all()

    queryset = queryset.filter(id=id)
    if queryset.exists():
        return True, queryset.first()
    return False, []


def get_random_product_item(*, product: Product) -> Union[Tuple[bool, List], Tuple[bool, ProductItem]]:
    items = product.items.filter(available=True)
    if items.exists():
        return True, choice(items)
    return False, []


def get_deals_list(*, user: User, queryset: Optional[QuerySet] = None, filters: Optional[dict] = None) -> QuerySet[Deal]:
    if not filters:
        filters = {}
    if queryset is None:
        queryset = Deal.objects.select_related("product_item", "product_item__product__owner").all()

    if user.account_type == User.SELLER:
        queryset = queryset.filter(product_item__product__owner=user)
    else:
        queryset = queryset.filter(buyer=user)

    return DealFilter(filters, queryset).qs
