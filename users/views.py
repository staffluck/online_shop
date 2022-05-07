from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from djoser.utils import login_user
from djoser.conf import settings
from djoser.serializers import TokenSerializer
from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema

from .services import EmailAuthorizationLetterProcessingService
from .serializers import EmailAuthenticationLetterSendInputSerializer
from .models import User, EmailAuthorizationLetter
from .selectors import get_user


@extend_schema(responses={200: None})
class EmailAuthorizationLetterSendView(GenericAPIView):

    def post(self, request):
        serializer = EmailAuthenticationLetterSendInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data["email"]
        is_exist, user = get_user(email=email)
        if is_exist and user.account_type != User.SELLER:
            auth_url = request.build_absolute_uri("/auth/email/{}/")
            email_letter, _ = EmailAuthorizationLetterProcessingService(
                user=user,
                to_email=email,
                auth_url=auth_url
            )

        return Response(status=200)


class EmailAuthorizationLetterProcessing(GenericAPIView):
    queryset = EmailAuthorizationLetter.objects.all()
    lookup_field = "uuid"

    def get(self, request, uuid):
        letter = self.get_object()

        if not letter.expire_on < timezone.now():
            user = letter.user
            token = login_user(request, user)
            token_serializer = settings.SERIALIZERS.token
            letter.delete()
            return Response(token_serializer(token).data, status=200)
        else:
            letter.delete()
            raise NotFound()


class TokenSchemaUpdate(OpenApiViewExtension):  # Отдельный файл? TODO
    target_class = "djoser.views.TokenCreateView"

    def view_replacement(self):

        @extend_schema(responses=TokenSerializer)
        class Fixed(self.target_class):
            pass
        return Fixed
