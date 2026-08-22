from collections.abc import Iterable

from store.models import Order


class VipDiscountRule:
    def calculate(self, order: Order) -> float | None:
        if order.customer.is_vip:
            return round(order.subtotal * 0.20, 2)
        return None


class BulkDiscountRule:
    def calculate(self, order: Order) -> float | None:
        if order.item_count >= 10:
            return round(order.subtotal * 0.10, 2)
        return None


class WelcomeCouponDiscountRule:
    def calculate(self, order: Order) -> float | None:
        if "WELCOME10" in order.coupons:
            return round(order.subtotal * 0.10, 2)
        return None


class DiscountCalculator:
    def __init__(self, rules: Iterable | None = None) -> None:
        if rules is None:
            rules = (
                VipDiscountRule(),
                BulkDiscountRule(),
                WelcomeCouponDiscountRule(),
            )
        self._rules = tuple(rules)

    def calculate(self, order: Order) -> float:
        for rule in self._rules:
            discount = rule.calculate(order)
            if discount is not None:
                return discount
        return 0.0