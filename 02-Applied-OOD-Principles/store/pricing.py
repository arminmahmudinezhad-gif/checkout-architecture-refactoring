from store.models import Order


class DiscountCalculator:
    def calculate(self, order: Order) -> float:
        subtotal = order.subtotal

        if order.customer.is_vip:
            discount = subtotal * 0.20
        elif order.item_count >= 10:
            discount = subtotal * 0.10
        elif "WELCOME10" in order.coupons:
            discount = subtotal * 0.10
        else:
            discount = 0.0

        return round(discount, 2)
