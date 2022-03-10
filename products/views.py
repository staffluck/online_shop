from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from .serializers import DealSerializer, ProductBuySerializer, ProductItemSerializer, ProductSerializer
from .models import Product, ProductItem, Deal
from .utils import simulate_request_to_kassa


class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filterset_fields = ['name', ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductItemAddToProductView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, pk):
        try:
            product = Product.objects.select_related("owner").get(id=pk)
        except Product.DoesNotExist:
            raise NotFound()
        if not product.owner == request.user:
            raise PermissionDenied()

        serializer = ProductItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)

        return Response(serializer.data, 200)


class ProductBuyView(APIView):

    def post(self, request, pk):
        try:
            product = Product.objects.select_related("owner").get(id=pk)
        except Product.DoesNotExist:
            raise NotFound()

        serializer = ProductBuySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data["email"]
        user_data = User.objects.get_or_create(email=email)  # username = ? TODO
        user = user_data[0]
        user_created = user_data[1]
        if user_created:
            user.set_password(User.objects.make_random_password())
            user.save()

        confirmation_url = request.build_absolute_uri("/products/deals/")
        kassa_request = simulate_request_to_kassa(confirmation_url, product.price)

        product_item = product.get_random_item()
        if not product_item:
            raise NotFound("Нет доступных товаров")

        product_item.available = False
        product_item.save()
        deal = Deal.objects.create(uuid=kassa_request["id"], buyer=user, product_item=product_item, cost=kassa_request["amount"]["value"])

        return Response(DealSerializer(instance=deal).data, status=200)


class DealListView(ListAPIView):
    serializer_class = DealSerializer

    def get_queryset(self):
        user = self.request.user
        if user.account_type == User.SELLER:
            return Deal.objects.filter(owner=user)
        return Deal.objects.filter(buyer=user)
