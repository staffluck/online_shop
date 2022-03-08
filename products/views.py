from rest_framework.generics import ListCreateAPIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProductItemSerializer, ProductSerializer
from .models import Product, ProductItem, Deal

class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['name', ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductItemAddToProductView(APIView):

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
