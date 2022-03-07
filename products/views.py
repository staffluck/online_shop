from rest_framework.generics import ListCreateAPIView

from .serializers import ProductSerializer
from .models import Product, ProductItem, Deal

class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['name', ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
