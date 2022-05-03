from django.contrib.auth.models import AbstractBaseUser

from users.models import User

from .models import Product, ProductItem, Deal
from .utils import simulate_request_to_kassa

def product_create(*, name: str, price: int, description: str, owner: AbstractBaseUser) -> Product:
    product = Product(
        name=name,
        price=price,
        description=description,
        owner=owner
    )

    product.full_clean()
    product.save()

    return product

def product_item_create(*, product: Product, text: str) -> ProductItem:
    product_item = ProductItem(
        text=text,
        product=product
    )

    product_item.full_clean()
    product_item.save()

    return product_item


def deal_create(*, confirmation_url: str, product: Product, product_item: ProductItem, buyer: User):
    kassa_request = simulate_request_to_kassa(confirmation_url, product.price)

    product_item.available = False
    product_item.save()
    deal = Deal.objects.create(uuid=kassa_request["id"], buyer=buyer, product_item=product_item, cost=kassa_request["amount"]["value"])

    return deal
