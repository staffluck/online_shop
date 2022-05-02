from django.contrib.auth.models import AbstractBaseUser

from .models import Product


def product_create(*, name: str, price: int, description: str, owner: AbstractBaseUser):
    product = Product(
        name=name,
        price=price,
        description=description,
        owner=owner
    )

    product.full_clean()
    product.save()

    return product
