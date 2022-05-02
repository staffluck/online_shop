from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Product, ProductItem, Deal
from users.models import User
from users.serializers import UserSerializer

class ProductInputSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(account_type=User.SELLER))

    class Meta:
        model = Product
        exclude = ["available", "purchased_count"]

class ProductOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    price = serializers.IntegerField(read_only=True)
    description = serializers.CharField(read_only=True)
    purchased_count = serializers.IntegerField(read_only=True)
    available = serializers.BooleanField(read_only=True)
    owner = UserSerializer(read_only=True)

class ProductItemSerializer(serializers.ModelSerializer):
    product = ProductOutputSerializer(read_only=True)

    class Meta:
        model = ProductItem
        exclude = ("available", )


class DealSerializer(serializers.ModelSerializer):
    product_item = serializers.SerializerMethodField()
    buyer = UserSerializer(read_only=True)

    class Meta:
        model = Deal
        fields = "__all__"  # exclude = ("uuid", ) в реальном проекте

    @extend_schema_field(ProductItemSerializer)
    def get_product_item(self, obj):
        if obj.status == "confirmed":
            return ProductItemSerializer(obj.product_item).data

        serializer = ProductOutputSerializer(obj.product_item.product)
        hidden_data = {
            "id": "-1",
            "product": serializer.data,
            "text": "-",
        }
        return hidden_data

class ProductBuySerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)


class DealStatusUpdateSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    status = serializers.CharField()
