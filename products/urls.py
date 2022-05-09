from django.urls import path

from .views import (
    ProductListCreateView, ProductItemAddToProductView, ProductBuyView, ProductDetailView,
    DealListView, DealStatusUpdateView, DealDetailView,
    ReviewListCreateView
)

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list-create"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("<int:pk>/add_item/", ProductItemAddToProductView.as_view(), name="product-add-item"),
    path("<int:pk>/buy/", ProductBuyView.as_view(), name="product-buy"),
    path("<int:pk>/reviews/", ReviewListCreateView.as_view(), name="review-list-create"),
    path("deals/", DealListView.as_view(), name="deal-list"),
    path("deals/<int:pk>/", DealDetailView.as_view(), name="deal-detail"),
    path("deals/update_status/", DealStatusUpdateView.as_view(), name="deal-update-status"),
]
