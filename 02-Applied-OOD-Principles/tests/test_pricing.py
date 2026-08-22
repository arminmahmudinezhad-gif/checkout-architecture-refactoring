import unittest
from unittest.mock import patch

from store.models import Customer, Order, OrderItem
from store.pricing import (
    BulkDiscountRule,
    DiscountCalculator,
    VipDiscountRule,
    WelcomeCouponDiscountRule,
)


class DiscountCalculatorTests(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(id=1, name="Customer", email="buyer@example.com")

    def make_order(self, *, is_vip=False, quantity=1, coupons=None, price=100.0):
        customer = Customer(
            id=self.customer.id,
            name=self.customer.name,
            email=self.customer.email,
            is_vip=is_vip,
        )
        return Order(
            id=1,
            customer=customer,
            payment_method="cash",
            items=[OrderItem(1, "Item", price, quantity)],
            coupons=coupons or [],
        )

    def test_vip_rule_short_circuits_bulk_and_coupon_rules(self):
        vip_rule = VipDiscountRule()
        bulk_rule = BulkDiscountRule()
        coupon_rule = WelcomeCouponDiscountRule()
        calculator = DiscountCalculator((vip_rule, bulk_rule, coupon_rule))
        order = self.make_order(is_vip=True, quantity=10, coupons=["WELCOME10"])

        with patch.object(vip_rule, "calculate", wraps=vip_rule.calculate) as vip:
            with patch.object(bulk_rule, "calculate", wraps=bulk_rule.calculate) as bulk:
                with patch.object(coupon_rule, "calculate", wraps=coupon_rule.calculate) as coupon:
                    discount = calculator.calculate(order)

        self.assertEqual(discount, 200.0)
        vip.assert_called_once_with(order)
        bulk.assert_not_called()
        coupon.assert_not_called()

    def test_bulk_rule_short_circuits_coupon_rule(self):
        vip_rule = VipDiscountRule()
        bulk_rule = BulkDiscountRule()
        coupon_rule = WelcomeCouponDiscountRule()
        calculator = DiscountCalculator((vip_rule, bulk_rule, coupon_rule))
        order = self.make_order(quantity=10, coupons=["WELCOME10"])

        with patch.object(vip_rule, "calculate", wraps=vip_rule.calculate) as vip:
            with patch.object(bulk_rule, "calculate", wraps=bulk_rule.calculate) as bulk:
                with patch.object(coupon_rule, "calculate", wraps=coupon_rule.calculate) as coupon:
                    discount = calculator.calculate(order)

        self.assertEqual(discount, 100.0)
        vip.assert_called_once_with(order)
        bulk.assert_called_once_with(order)
        coupon.assert_not_called()

    def test_coupon_applies_when_it_is_the_only_matching_rule(self):
        order = self.make_order(coupons=["WELCOME10"])

        self.assertEqual(DiscountCalculator().calculate(order), 10.0)

    def test_returns_zero_when_no_rule_matches(self):
        order = self.make_order()

        self.assertEqual(DiscountCalculator().calculate(order), 0.0)

    def test_discount_is_rounded_to_two_decimal_places(self):
        order = self.make_order(coupons=["WELCOME10"], quantity=3, price=12.37)

        self.assertEqual(DiscountCalculator().calculate(order), 3.71)


if __name__ == "__main__":
    unittest.main()
