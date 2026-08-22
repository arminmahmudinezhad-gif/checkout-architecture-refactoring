from collections.abc import Iterable

from store.contracts import PaymentHandler
from store.models import Order


class CreditCardPaymentHandler:
    method = "credit_card"

    def process(self, order: Order, amount: float) -> str:
        card = order.customer.credit_card
        print(f"[payment] Charging card {card} {amount:.2f}")
        return f"paid_by_credit_card:{amount:.2f}"


class PayPalPaymentHandler:
    method = "paypal"

    def process(self, order: Order, amount: float) -> str:
        email = order.customer.email
        print(f"[payment] Charging PayPal {email} {amount:.2f}")
        return f"paid_by_paypal:{amount:.2f}"


class BitcoinPaymentHandler:
    method = "bitcoin"

    def process(self, order: Order, amount: float) -> str:
        address = order.customer.bitcoin_address
        print(f"[payment] Charging BTC {address} {amount:.2f}")
        return f"paid_by_bitcoin:{amount:.2f}"


class CashPaymentHandler:
    method = "cash"

    def process(self, order: Order, amount: float) -> str:
        print(f"[payment] Accepting cash {amount:.2f}")
        return f"paid_by_cash:{amount:.2f}"


class PaymentProcessor:
    def __init__(self, handlers: Iterable[PaymentHandler]):
        self._handlers = {handler.method: handler for handler in handlers}

    def process(self, order: Order, amount: float) -> str:
        try:
            handler = self._handlers[order.payment_method]
        except KeyError:
            raise ValueError(
                f"Unknown payment method: {order.payment_method!r}"
            ) from None
        return handler.process(order, amount)
