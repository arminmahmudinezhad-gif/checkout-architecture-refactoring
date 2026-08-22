from typing import Protocol

from store.models import Order


class PaymentHandler(Protocol):
    method: str

    def process(self, order: Order, amount: float) -> str:
        ...


class PricingCalculator(Protocol):
    def calculate(self, order: Order) -> float:
        ...


class OrderRepository(Protocol):
    def save_order(self, order: Order) -> None:
        ...

    def load_order(self, order_id: int):
        ...


class Notifier(Protocol):
    def send(self, customer, message: str) -> None:
        ...