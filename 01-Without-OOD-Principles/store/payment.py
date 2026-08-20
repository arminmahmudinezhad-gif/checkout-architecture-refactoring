from store.models import Order


class PaymentProcessor:
    def process(self, order: Order, amount: float) -> str:
        method = order.payment_method

        if method == "credit_card":
            card = order.customer.credit_card
            print(f"[payment] Charging card {card} {amount:.2f}")
            return f"paid_by_credit_card:{amount:.2f}"

        elif method == "paypal":
            email = order.customer.email
            print(f"[payment] Charging PayPal {email} {amount:.2f}")
            return f"paid_by_paypal:{amount:.2f}"

        elif method == "bitcoin":
            address = order.customer.bitcoin_address
            print(f"[payment] Charging BTC {address} {amount:.2f}")
            return f"paid_by_bitcoin:{amount:.2f}"

        else:
            raise ValueError(f"Unknown payment method: {method!r}")
