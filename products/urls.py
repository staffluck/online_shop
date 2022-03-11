from django.urls import path

from .views import ProductListCreateView, ProductItemAddToProductView, ProductBuyView, DealListView, DealStatusUpdateView

urlpatterns = [
    path("", ProductListCreateView.as_view(), ),
    path("<int:pk>/add_item/", ProductItemAddToProductView.as_view(), ),
    path("<int:pk>/buy/", ProductBuyView.as_view(), ),
    path("deals/", DealListView.as_view(), ),
    path('deals/update_status/', DealStatusUpdateView.as_view())
]
