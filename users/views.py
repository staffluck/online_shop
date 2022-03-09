from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import EmailAuthenticationLetterSendSerializer
from .models import User, EmailAuthorizationLetter


class EmailAuthorizationLetterSendView(APIView):

    def post(self, request):
        serializer = EmailAuthenticationLetterSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            try:
                EmailAuthorizationLetter.objects.get(user=user)
            except EmailAuthorizationLetter.DoesNotExist:
                pass
            else:
                EmailAuthorizationLetter.objects.get(user=user).delete()

            email_letter = EmailAuthorizationLetter.objects.create(user=user)
            uuid = email_letter.uuid
            email_auth_uri = request.build_absolute_uri("/auth/email/{}/".format(uuid))

            subject = "Test"
            message = "{}".format(email_auth_uri)
            send_mail(subject, message, "from@test.ru", ["to@test.ru", ])

        return Response(status=200)
