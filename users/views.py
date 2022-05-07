from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from djoser.utils import login_user
from djoser.conf import settings as djoser_settings
from djoser.serializers import TokenSerializer
from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema

from .services import EmailAuthorizationLetterSendService, EmailAuthorizationLetterProccessingService
from .serializers import EmailAuthenticationLetterSendInputSerializer
from .models import User
from .selectors import get_user


@extend_schema(responses={200: None})
class EmailAuthorizationLetterSendView(GenericAPIView):

    def post(self, request):
        serializer = EmailAuthenticationLetterSendInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data["email"]
        is_exist, user = get_user(email=email)
        if is_exist and user.account_type != User.SELLER:
            auth_url = request.build_absolute_uri("/auth/email/")
            email_service = EmailAuthorizationLetterSendService(
                user=user,
                to_email=email,
                auth_url=auth_url
            )
            email_letter, _ = email_service.execute()

        return Response(status=200)


class EmailAuthorizationLetterProcessingView(GenericAPIView):

    def get(self, request, uuid):
        email_service = EmailAuthorizationLetterProccessingService(letter_uuid=uuid)
        user = email_service.execute()
        if not user:
            raise NotFound()

        token = login_user(request, user)
        token_serializer = djoser_settings.SERIALIZERS.token
        serializer_output = token_serializer(token)
        return Response(serializer_output.data, status=200)


class TokenSchemaUpdate(OpenApiViewExtension):  # Отдельный файл? TODO
    target_class = "djoser.views.TokenCreateView"

    def view_replacement(self):

        @extend_schema(responses=TokenSerializer)
        class Fixed(self.target_class):
            pass
        return Fixed
