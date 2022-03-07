from django.db import models
from users.models import User

class Product(models.Model):
    owner = models.ForeignKey(User, models.SET_NULL, related_name="owned_products", verbose_name="Владелец", null=True)
    name = models.CharField("Название", max_length=75, db_index=True)
    price = models.IntegerField("Цена", db_index=True)
    description = models.TextField("Описание", max_length=1000)
    purchased_count = models.IntegerField("Количество купленных копий", default=0)


class ProductItem(models.Model):
    product = models.ForeignKey(Product, models.SET_NULL, related_name="items", verbose_name="Продукт", null=True)
    text = models.TextField("Текстовый вариант товара", max_length=100)

    # file = todo


class Deal(models.Model):
    product_item = models.OneToOneField(ProductItem, models.CASCADE, related_name="deal", verbose_name="Предмет Продукта")
    buyer = models.ForeignKey(User, models.SET_NULL, related_name="deals", verbose_name="Покупатель", null=True)
    cost = models.IntegerField("Итоговая стоимость")

    # messages = todo
