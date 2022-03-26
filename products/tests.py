from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import Product
from users.models import User

class ProductTests(APITestCase):

    @classmethod
    def setUpTestData(self):
        self.correct_seller_data = {
            "email": "TestSeller@email.test",
            "password": "qwertyMoreThan8"
        }
        self.correct_buyer_data = {
            "email": "TestBuyer@email.test",
            "password": "qwertyMoreThan8"
        }
        self.correct_product_data = {
            "name": "ProductTest1",
            "price": 100,
            "description": "ProductDescription1"
        }
        self.wrong_product_data = {
            "name": "ProductTest1",
            "description": "ProductDescription1"
        }
        self.correct_product_item_data = {
            "text": "ProductItemTest"
        }

        self.product_create_url = reverse("product-list")
        self.product_add_item_url = reverse("product-add-item", kwargs={"pk": 1})

        self.seller = User.objects.create_user(account_type=User.SELLER, **self.correct_seller_data)
        self.wrong_seller = User.objects.create_user(account_type=User.SELLER, email="TestWrongSeller1@email.test", password="qwertyMoreThan8")
        self.buyer = User.objects.create_user(account_type=User.BUYER, **self.correct_buyer_data)

    def test_correct_create_product(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.post(self.product_create_url, self.correct_product_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.last().owner, self.seller)

    def test_wrong_data_create_product(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.post(self.product_create_url, self.wrong_product_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.all().count(), 0)

    def test_unauthorized_create_product(self):
        response = self.client.post(self.product_create_url, self.wrong_product_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.all().count(), 0)

    def test_correct_add_item(self):
        self.client.force_authenticate(user=self.seller)
        product = Product.objects.create(owner=self.seller, **self.correct_product_data)

        response = self.client.post(self.product_add_item_url, self.correct_product_item_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_and_not_seller_add_item(self):
        self.client.force_authenticate(user=self.wrong_seller)
        product = Product.objects.create(owner=self.seller, **self.correct_product_data)

        response_wrong_seller = self.client.post(self.product_add_item_url, self.correct_product_item_data)
        self.client.force_authenticate(user=None)
        response_unauthenticated = self.client.post(self.product_add_item_url, self.correct_product_item_data)

        self.assertEqual(response_unauthenticated.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_wrong_seller.status_code, status.HTTP_403_FORBIDDEN)
