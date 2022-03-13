from smtplib import SMTPException

from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from djoser.utils import login_user
from djoser.conf import settings
from djoser.serializers import TokenSerializer
from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema


from .serializers import EmailAuthenticationLetterSendSerializer
from .models import User, EmailAuthorizationLetter


@extend_schema(responses={200: None})
class EmailAuthorizationLetterSendView(GenericAPIView):
    serializer_class = EmailAuthenticationLetterSendSerializer

    def post(self, request):
        serializer = EmailAuthenticationLetterSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user and user.account_type != User.SELLER:
            try:
                EmailAuthorizationLetter.objects.get(user=user).delete()
            except EmailAuthorizationLetter.DoesNotExist:
                pass

            email_letter = EmailAuthorizationLetter.objects.create(user=user)
            uuid = email_letter.uuid
            email_auth_uri = request.build_absolute_uri("/auth/email/{}/".format(uuid))

            subject = "Test"
            message = "{}".format(email_auth_uri)
            try:
                send_mail(subject, message, "maybebaybeboy4ik@mail.ru", [email, ])
            except SMTPException:
                return Response("Невозможно отправить письмо", 400)
        return Response(status=200)


class EmailAuthorizationLetterProcessing(GenericAPIView):

    def get(self, request, uuid):
        try:
            letter = EmailAuthorizationLetter.objects.get(uuid=uuid)
        except EmailAuthorizationLetter.DoesNotExist:
            raise NotFound()

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
