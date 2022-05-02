from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.serializers import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.types import OpenApiTypes
import django_filters

from common.pagination import get_paginated_response, get_paginated_response_schema
from users.models import User
from users.permissions import IsOwner, IsSeller, ReadOnly
from .serializers import (
    DealSerializer, DealStatusUpdateSerializer,
    ProductBuyInputSerializer,
    ProductInputSerializer, ProductOutputSerializer,
    ProductItemInputSerializer, ProductItemOutputSerializer,
)
from .selectors import get_product_by_id, get_products_list
from .services import product_create, product_item_create
from .models import Product, ProductItem, Deal
from .utils import simulate_request_to_kassa


class ProductListCreateView(GenericAPIView):
    serializer_class = ProductOutputSerializer
    permission_classes = [IsAuthenticated, IsSeller | ReadOnly]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class ProductFilterSerializer(serializers.Serializer):
        limit = serializers.IntegerField(required=False)
        offset = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)
        mine = serializers.BooleanField(required=False)

    @extend_schema(
        request=ProductInputSerializer
    )
    def post(self, request):
        serializer_input = ProductInputSerializer(data=request.data)
        serializer_input.is_valid(raise_exception=True)

        product = product_create(owner=request.user, **serializer_input.validated_data)

        output_serializer = ProductOutputSerializer(instance=product)
        return Response(output_serializer.data, status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            ProductFilterSerializer,
        ],
        responses=get_paginated_response_schema(ProductOutputSerializer)
    )
    def get(self, request):
        queryset = get_products_list(
            request=request,
            queryset=Product.objects.filter(available=True),
            filters=request.query_params
        )
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=ProductOutputSerializer,
            queryset=queryset,
            request=request,
            view=self
        )

class ProductItemAddToProductView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ProductItemOutputSerializer

    @extend_schema(
        request=ProductItemInputSerializer
    )
    def post(self, request, pk):
        is_exists, product = get_product_by_id(id=pk)
        if not is_exists:
            raise NotFound()
        self.check_object_permissions(request, product)

        serializer_input = ProductItemInputSerializer(data=request.data)
        serializer_input.is_valid(raise_exception=True)
        product_item = product_item_create(
            product=product,
            **serializer_input.data
        )

        serializer_output = ProductItemOutputSerializer(instance=product_item)
        return Response(serializer_output.data, status.HTTP_201_CREATED)


class ProductBuyView(GenericAPIView):
    serializer_class = DealSerializer

    @extend_schema(
        responses={201: DealSerializer}
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
