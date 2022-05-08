from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.serializers import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from drf_spectacular.utils import extend_schema

from common.pagination import get_paginated_response, get_paginated_response_schema
from common.selectors_services import get_or_create_buyer_user
from users.permissions import IsOwner, IsSeller, ReadOnly
from .serializers import (
    DealOutputSerializer,
    DealStatusUpdateInputSerializer,
    ProductBuyInputSerializer,
    ProductInputSerializer, ProductOutputSerializer,
    ProductItemInputSerializer, ProductItemOutputSerializer,
    ReviewOutputSerializer
)
from .selectors import get_deal_by_uuid, get_deals_list, get_product_by_id, get_products_list, get_random_product_item, get_reviews_list
from .services import deal_create, deal_update_status, product_create, product_item_create
from .models import Product, Deal, Review


class ProductListCreateView(GenericAPIView):
    serializer_class = ProductOutputSerializer
    permission_classes = [(IsAuthenticated & IsSeller) | ReadOnly]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterSerializer(serializers.Serializer):
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
            FilterSerializer,
        ],
        responses=get_paginated_response_schema(ProductOutputSerializer)
    )
    def get(self, request):
        queryset = get_products_list(
            request=request,
            queryset=Product.objects.select_related("owner").filter(available=True),
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
        product_item = product_item_create(product=product, **serializer_input.data)

        serializer_output = ProductItemOutputSerializer(instance=product_item)
        return Response(serializer_output.data, status.HTTP_201_CREATED)


class ProductBuyView(GenericAPIView):
    serializer_class = DealOutputSerializer

    @extend_schema(
        request=ProductBuyInputSerializer
    )
    def post(self, request, pk):
        if not request.user.is_authenticated:
            serializer = ProductBuyInputSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.data.get("email")
            if not email:
                raise ValidationError({"email": ["This field is required."]})

            user = get_or_create_buyer_user(email=email)
        else:
            user = request.user

        is_exist, product = get_product_by_id(id=pk)
        if not is_exist:
            raise NotFound()
        is_exist, product_item = get_random_product_item(product=product)
        if not product_item:
            raise NotFound("Нет доступных товаров")

        confirmation_url = request.build_absolute_uri("/products/deals/")
        deal = deal_create(
            confirmation_url=confirmation_url,
            product=product,
            product_item=product_item,
            buyer=user
        )

        serializer_output = DealOutputSerializer(instance=deal)
        return Response(serializer_output.data, status=status.HTTP_201_CREATED)


class DealListView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterSerializer(serializers.Serializer):
        limit = serializers.IntegerField(required=False)
        offset = serializers.IntegerField(required=False)
        status = serializers.CharField(required=False)

    @extend_schema(
        parameters=[
            FilterSerializer
        ],
        responses=get_paginated_response_schema(DealOutputSerializer)
    )
    def get(self, request):
        deals = get_deals_list(
            user=request.user,
            filters=request.query_params
        )
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=DealOutputSerializer,
            queryset=deals,
            request=request,
            view=self
        )


class DealStatusUpdateView(GenericAPIView):
    serializer_class = DealStatusUpdateInputSerializer

    @extend_schema(responses={200: None})
    def post(self, request):
        serializer_input = DealStatusUpdateInputSerializer(data=request.data)
        serializer_input.is_valid(raise_exception=True)

        validated_data = serializer_input.validated_data
        is_exist, deal = get_deal_by_uuid(
            uuid=validated_data["uuid"],
            queryset=Deal.objects.select_related("product_item", "product_item__product")
        )
        if not is_exist:
            return Response(status=400)
        deal_update_status(
            deal=deal,
            uuid=validated_data["uuid"],
            status=validated_data["status"]
        )

        return Response(status=200)


class ReviewListCreateView(GenericAPIView):

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterSerializer(serializers.Serializer):
        limit = serializers.IntegerField(required=False)
        offset = serializers.IntegerField(required=False)
        review_type = serializers.IntegerField(required=False)
        product_id = serializers.IntegerField()

    @extend_schema(
        parameters=[
            FilterSerializer,
        ],
        responses=get_paginated_response_schema(ReviewOutputSerializer)
    )
    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        queryset = get_reviews_list(filters=filters_serializer.validated_data)
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=ReviewOutputSerializer,
            queryset=queryset,
            request=request,
            view=self
        )
