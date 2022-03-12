from random import choice

from django.db import models
from django.dispatch import receiver

from users.models import User

class Product(models.Model):
    owner = models.ForeignKey(User, models.SET_NULL, related_name="owned_products", verbose_name="Владелец", null=True)
    name = models.CharField("Название", max_length=75, db_index=True)
    price = models.IntegerField("Цена", db_index=True)
    description = models.TextField("Описание", max_length=1000)
    purchased_count = models.IntegerField("Количество купленных копий", default=0)
    available = models.BooleanField(default=False)

    def get_random_item(self):
        #  TODO проверить другие способы рандома. order_by(?) не вариант
        items = self.items.filter(available=True)
        if items:
            return choice(items)
        return False

class ProductItem(models.Model):
    product = models.ForeignKey(Product, models.SET_NULL, related_name="items", verbose_name="Продукт", null=True)
    text = models.TextField("Текстовый вариант товара", max_length=100)
    available = models.BooleanField(default=True)

    # file = todo

@receiver(models.signals.post_save, sender=ProductItem)
def product_set_to_available(sender, **kwargs):
    product = sender.product
    if not product.available:
        product.available = True
        product.save(update_fields=["available"])


class Deal(models.Model):
    uuid = models.UUIDField()
    product_item = models.OneToOneField(ProductItem, models.CASCADE, related_name="deal", verbose_name="Предмет Продукта")
    payment_confirmed = models.BooleanField(default=False)
    buyer = models.ForeignKey(User, models.SET_NULL, related_name="deals", verbose_name="Покупатель", null=True)
    cost = models.IntegerField("Итоговая стоимость")

    # messages = todo
