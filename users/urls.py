from django.urls import path, include

from .views import EmailAuthorizationLetterSendView, EmailAuthorizationLetterProcessingView

urlpatterns = [
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
    path("email/", EmailAuthorizationLetterSendView.as_view(), ),
    path("email/<uuid:uuid>/", EmailAuthorizationLetterProcessingView.as_view(), )
]
