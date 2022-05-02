from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.serializers import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from drf_spectacular.utils import extend_schema
import django_filters

from users.models import User
from users.permissions import IsOwner, IsSeller, ReadOnly
from users.serializers import UserSerializer
from .serializers import (
    DealSerializer, DealStatusUpdateSerializer, ProductBuySerializer, ProductItemSerializer,
    ProductInputSerializer, ProductOutputSerializer
)
from .models import Product, ProductItem, Deal
from .utils import simulate_request_to_kassa


class ProductListCreateView(GenericAPIView):
    serializer_class = ProductOutputSerializer
    queryset = Product.objects.filter(available=True)
    permission_classes = [IsAuthenticated, IsSeller | ReadOnly]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

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

    def post(self, request):
        serializer_data = request.data
        serializer_data["owner"] = request.user.id
        product_serializer = ProductInputSerializer(data=serializer_data)
        product_serializer.is_valid(raise_exception=True)

        product = Product(**product_serializer.validated_data)
        product.full_clean()
        product.save()

        output_serializer = ProductOutputSerializer(instance=product)
        return Response(output_serializer.data, status.HTTP_201_CREATED)

    def get(self, request):
        queryset = self.ProductFilter(request.query_params, self.get_queryset(), request=request).qs
        paginator = self.Pagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page:
            serializer = ProductOutputSerializer(page, many=True)
        else:
            serializer = ProductOutputSerializer(queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

class ProductItemAddToProductView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ProductItemSerializer

    def post(self, request, pk):
        try:
            product = Product.objects.select_related("owner").get(id=pk)
            self.check_object_permissions(request, product)
        except Product.DoesNotExist:
            raise NotFound()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)

        return Response(serializer.data, 201)


class ProductBuyView(GenericAPIView):
    serializer_class = ProductBuySerializer
    queryset = Product.objects.filter(available=True)

    @extend_schema(
        responses={201: DealSerializer, 404: None}
    )
    def post(self, request, pk):
        if not request.user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid()
            email = serializer.data.get("email")
            if not email:
                raise ValidationError({"email": "Обязательное поле"})

            user = User(email=email, account_type=User.BUYER)
            user.set_password(User.objects.make_random_password())
            user.save()
        else:
            email = request.user.email
            user = request.user

        product = self.get_object()
        product_item = product.get_random_item()
        if not product_item:
            raise NotFound("Нет доступных товаров")

        confirmation_url = request.build_absolute_uri("/products/deals/")
        kassa_request = simulate_request_to_kassa(confirmation_url, product.price)

        product_item.available = False
        product_item.save()
        deal = Deal.objects.create(uuid=kassa_request["id"], buyer=user, product_item=product_item, cost=kassa_request["amount"]["value"])

        return Response(DealSerializer(instance=deal).data, status=200)


class DealListView(ListAPIView):
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Deal.objects.none()
        user = self.request.user
        if user.account_type == User.SELLER:
            return Deal.objects.filter(product_item__product__owner=user)
        return Deal.objects.filter(buyer=user)


class DealStatusUpdateView(GenericAPIView):
    serializer_class = DealStatusUpdateSerializer

    @extend_schema(responses={200: None})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        try:
            deal = Deal.objects.get(uuid=data["uuid"])
        except Deal.DoesNotExist:
            raise NotFound()

        product = deal.product_item.product
        if data["status"] == "confirmed":
            deal.status = "confirmed"
            product.purchased_count += 1
            product.save()
            deal.save()
        elif data["status"] == "canceled":
            product_item = deal.product_item
            product_item.available = True
            product_item.save()
            deal.delete()  # TODO: Архив сделок

        return Response(status=200)
