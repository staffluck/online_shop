from django.contrib.auth.models import AbstractBaseUser

from .models import Product, ProductItem


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
