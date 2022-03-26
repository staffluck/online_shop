from django.urls import path

from .views import ProductListCreateView, ProductItemAddToProductView, ProductBuyView, DealListView, DealStatusUpdateView

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list"),
    path("<int:pk>/add_item/", ProductItemAddToProductView.as_view(), name="product-add-item"),
    path("<int:pk>/buy/", ProductBuyView.as_view(), name="product-buy"),
    path("deals/", DealListView.as_view(), name="deal-list"),
    path('deals/update_status/', DealStatusUpdateView.as_view(), name="deal-update-status")
]
