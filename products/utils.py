from uuid import uuid4


def simulate_request_to_kassa(confirmation_url, value):
    uuid = uuid4()
    response = {
        "id": uuid,
        "amount": {
            "value": value,
            "currency": "RUB"
        },
        "confirmation_url": confirmation_url
    }

    return response
