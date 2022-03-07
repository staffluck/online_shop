from rest_framework import serializers
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
        fields = "__all__"


class DealSerializer(serializers.ModelSerializer):
    product_item = ProductItemSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)

    class Meta:
        model = Deal
        fields = "__all__"
