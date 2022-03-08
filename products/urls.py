from django.urls import path

from .views import ProductListCreateView, ProductItemAddToProductView

urlpatterns = [
    path("", ProductListCreateView.as_view(), ),
    path("<int:pk>/add_item/", ProductItemAddToProductView.as_view(), )
]
