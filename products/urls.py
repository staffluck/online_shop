from django.urls import path

from .views import ProductListCreateView

urlpatterns = [
    path("", ProductListCreateView.as_view(), )
]