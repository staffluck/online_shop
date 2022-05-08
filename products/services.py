from django.contrib.auth.models import AbstractBaseUser

from users.models import User

from .models import Product, ProductItem, Deal, Review
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


def deal_update_status(*, deal: Deal, status: str) -> None:
    product_item = deal.product_item
    product = product_item.product

    if status == "confirmed":
        deal.status = Deal.CONFIRMED
        product.purchased_count += 1
        product.save()
        deal.save()
    elif status == "canceled":
        product_item.available = True
        product_item.save()
        deal.delete()

    return None


def review_create(*, text: str, review_type: str) -> Review:
    review = Review(
        text=text,
        review_type=review_type
    )

    review.full_clean()
    review.save()

    return review
