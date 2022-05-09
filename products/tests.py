import json

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.conf import settings

from .models import Product, Deal, ProductItem
from users.models import User


class ProductTests(APITestCase):
    # TODO: Faker, factory?

    @classmethod
    def setUpTestData(self):
        self.correct_seller_data = {
            "email": "TestSeller@email.test",
            "password": "qwertyMoreThan8"
        }
        self.wrong_seller_data = {
            "email": "TestWrongSeller1@email.test",
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
        self.update_status_data = {
            "uuid": "{}",
            "status": "confirmed"
        }

        self.product_create_url = reverse("product-list-create")
        self.deal_update_status = reverse("deal-update-status")

        settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

        self.seller = User.objects.create_user(account_type=User.AccountTypes.SELLER, **self.correct_seller_data)
        self.wrong_seller = User.objects.create_user(account_type=User.AccountTypes.SELLER, **self.wrong_seller_data)
        self.buyer = User.objects.create_user(account_type=User.AccountTypes.BUYER, **self.correct_buyer_data)

        self.product = Product.objects.create(owner=self.seller, **self.correct_product_data)
        self.product_item = ProductItem.objects.create(product=self.product, text={"TestItem"})
        self.product_add_item_url = reverse("product-add-item", kwargs={"pk": self.product.id})
        self.product_buy_url = reverse("product-buy", kwargs={"pk": self.product.id})

    def test_correct_create_product(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.post(self.product_create_url, self.correct_product_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.last().owner, self.seller)

    def test_wrong_data_create_product(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.post(self.product_create_url, self.wrong_product_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.all().count(), 1)  # setUpTestData создаёт 1 product

    def test_unauthorized_create_product(self):
        response = self.client.post(self.product_create_url, self.wrong_product_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.all().count(), 1)  # setUpTestData создаёт 1 product

    def test_correct_add_item(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(self.product_add_item_url, self.correct_product_item_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_and_not_seller_add_item(self):
        self.client.force_authenticate(user=self.wrong_seller)

        response_wrong_seller = self.client.post(self.product_add_item_url, self.correct_product_item_data)
        self.client.force_authenticate(user=None)
        response_unauthenticated = self.client.post(self.product_add_item_url, self.correct_product_item_data)

        self.assertEqual(response_unauthenticated.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_wrong_seller.status_code, status.HTTP_403_FORBIDDEN)

    def test_correct_buy_and_confirm_product(self):
        self.client.force_authenticate(user=self.buyer)

        response = self.client.post(self.product_buy_url)
        deal_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deal_data["product_item"]["id"], "-1")

        confirm_data = self.update_status_data
        confirm_data["uuid"] = deal_data["uuid"]
        response_confirm = self.client.post(self.deal_update_status, confirm_data)
        deal = Deal.objects.get(uuid=deal_data["uuid"])

        self.assertEqual(response_confirm.status_code, status.HTTP_200_OK)
        self.assertEqual(deal.status, "confirmed")
