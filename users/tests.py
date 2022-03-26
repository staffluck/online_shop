from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import User


class UserTests(APITestCase):

    @classmethod
    def setUpTestData(self):
        self.correct_user_data = {
            "email": "Test@email.test",
            "password": "qwertyMoreThan8"
        }

        self.user_list_url = reverse("user-list")

    def test_correct_create_user(self):
        response = self.client.post(self.user_list_url, self.correct_user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 1)

    def test_wrong_data_create_user(self):
        user = User.objects.create(**self.correct_user_data)
        response_repeated = self.client.post(self.user_list_url, self.correct_user_data)

        self.assertEqual(response_repeated.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.all().count(), 1)


class TokenTests(APITestCase):

    @classmethod
    def setUpTestData(self):
        self.correct_user_data = {
            "email": "Test@email.test",
            "password": "qwertyMoreThan8"
        }

        self.token_login_url = reverse("login")

        self.user = User.objects.create_user(**self.correct_user_data)

    def test_correct_login(self):
        response = self.client.post(self.token_login_url, self.correct_user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_data_login(self):
        response = self.client.post(self.token_login_url, {"email": "Test@email.test", "password": "111"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
