from typing import Protocol

from store.models import Order


class PaymentHandler(Protocol):
    method: str

    def process(self, order: Order, amount: float) -> str:
        ...
