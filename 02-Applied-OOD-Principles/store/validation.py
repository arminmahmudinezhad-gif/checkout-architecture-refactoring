from store.models import BundleOrder, Order


class OrderValidator:
    def validate(self, order: Order) -> None:
        if not order.items and not isinstance(order, BundleOrder):
            raise ValueError("Order has no items")
        if not order.payment_method:
            raise ValueError("Order has no payment method")