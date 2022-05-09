from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Product, Deal
from users.serializers import UserSerializer


class ProductInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ["available", "purchased_count", "owner"]


class ProductOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    description = serializers.CharField()
    purchased_count = serializers.IntegerField()
    available = serializers.BooleanField()
    negative_reviews_count = serializers.IntegerField()
    positive_reviews_count = serializers.IntegerField()
    owner = UserSerializer()


class ProductItemInputSerializer(serializers.Serializer):
    text = serializers.CharField()


class ProductItemOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    available = serializers.BooleanField()
    product_id = serializers.IntegerField()


class DealOutputSerializer(serializers.ModelSerializer):
    product_item = serializers.SerializerMethodField()
    buyer = UserSerializer()

    class Meta:
        model = Deal
        fields = "__all__"  # exclude = ("uuid", ) в реальном проекте

    @extend_schema_field(ProductOutputSerializer)
    def get_product_item(self, obj):
        if not obj.status == Deal.CONFIRMED:
            obj.product_item.id = -1
            obj.product_item.text = "-"
        return ProductItemOutputSerializer(obj.product_item).data


class ProductBuyInputSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)


class DealStatusUpdateInputSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    status = serializers.CharField()


class ReviewInputSerializer(serializers.Serializer):
    review_type = serializers.IntegerField(min_value=0, max_value=1)
    text = serializers.CharField()


class ReviewOutputSerializer(serializers.Serializer):
    review_type = serializers.IntegerField()
    text = serializers.CharField()
