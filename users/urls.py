from django.urls import path, include

from .views import EmailAuthorizationLetterSendView

urlpatterns = [
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
    path("email/", EmailAuthorizationLetterSendView.as_view(), ),
]
