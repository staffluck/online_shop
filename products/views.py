from rest_framework.generics import ListCreateAPIView, ListAPIView, GenericAPIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from drf_spectacular.utils import extend_schema

from users.models import User
from .serializers import DealSerializer, DealStatusUpdateSerializer, ProductBuySerializer, ProductItemSerializer, ProductSerializer
from .models import Product, ProductItem, Deal
from .utils import simulate_request_to_kassa


class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filterset_fields = ['name', ]

    def post(self, request, *args, **kwargs):
        if request.user.account_type == User.BUYER:
            raise PermissionDenied()
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductItemAddToProductView(GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ProductItemSerializer

    def post(self, request, pk):
        try:
            product = Product.objects.select_related("owner").get(id=pk)
        except Product.DoesNotExist:
            raise NotFound()
        if not product.owner == request.user:
            raise PermissionDenied()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)

        return Response(serializer.data, 200)


class ProductBuyView(GenericAPIView):
    serializer_class = ProductBuySerializer

    @extend_schema(
        responses={201: DealSerializer, 404: None}
    )
    def post(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            raise NotFound()

        product_item = product.get_random_item()
        if not product_item:
            raise NotFound("Нет доступных товаров")

        if not request.user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid()
            email = serializer.data.get("email")
            if not email:
                raise ValidationError({"email": "Обязательное поле"})
        else:
            email = request.user.email

        user_data = User.objects.get_or_create(email=email, defaults={"username": email, "account_type": 0})  # username = ? TODO
        user = user_data[0]
        user_created = user_data[1]
        if user_created:
            user.set_password(User.objects.make_random_password())
            user.save()

        confirmation_url = request.build_absolute_uri("/products/deals/")
        kassa_request = simulate_request_to_kassa(confirmation_url, product.price)

        product_item.available = False
        product_item.save()
        deal = Deal.objects.create(uuid=kassa_request["id"], buyer=user, product_item=product_item, cost=kassa_request["amount"]["value"])

        return Response(DealSerializer(instance=deal).data, status=200)


class DealListView(ListAPIView):
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]

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
            deal.delete()

        return Response(status=200)
