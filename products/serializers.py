from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Product, ProductItem, Deal
from users.serializers import UserSerializer


class ProductSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ['purchased_count', ]


class ProductItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductItem
        exclude = ("available", )


class DealSerializer(serializers.ModelSerializer):
    product_item = serializers.SerializerMethodField()
    buyer = UserSerializer(read_only=True)

    class Meta:
        model = Deal
        fields = "__all__"

    @extend_schema_field(ProductItemSerializer)
    def get_product_item(self, obj):
        if obj.payment_confirmed:
            return ProductItemSerializer(obj.product_item).data

        serializer = ProductSerializer(obj.product_item.product)
        hidden_data = {
            "text": "-",
            "id": "-1",
            "product": serializer.data
        }
        return hidden_data

class ProductBuySerializer(serializers.Serializer):
    email = serializers.EmailField()
