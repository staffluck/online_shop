from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Product, Deal
from users.serializers import UserSerializer


class ProductInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ["available", "purchased_count", "owner", "reviews"]


class ProductOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    description = serializers.CharField()
    purchased_count = serializers.IntegerField()
    available = serializers.BooleanField()
    owner = UserSerializer()


class ProductItemInputSerializer(serializers.Serializer):
    text = serializers.CharField()


class ProductItemOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    available = serializers.BooleanField()


class DealOutputSerializer(serializers.ModelSerializer):
    product_item = serializers.SerializerMethodField()
    buyer = UserSerializer()

    class Meta:
        model = Deal
        fields = "__all__"  # exclude = ("uuid", ) в реальном проекте

    @extend_schema_field(ProductOutputSerializer)
    def get_product_item(self, obj):
        if obj.status == "confirmed":
            return ProductOutputSerializer(obj.product_item).data

        serializer = ProductOutputSerializer(obj.product_item.product)
        hidden_data = {
            "id": "-1",
            "product": serializer.data,
            "text": "-",
        }
        return hidden_data


class ProductBuyInputSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)


class DealStatusUpdateInputSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    status = serializers.CharField()
