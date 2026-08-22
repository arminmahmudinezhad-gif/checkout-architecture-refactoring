import unittest

from store.models import BundleOrder, Customer, Order, OrderItem
from store.validation import OrderValidator


class OrderValidatorTests(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(id=1, name="Customer", email="buyer@example.com")
        self.validator = OrderValidator()

    def test_empty_ordinary_order_is_rejected(self):
        order = Order(id=1, customer=self.customer, payment_method="cash")

        with self.assertRaisesRegex(ValueError, "^Order has no items$"):
            self.validator.validate(order)

    def test_empty_bundle_order_with_payment_method_is_allowed(self):
        order = BundleOrder(id=2, customer=self.customer, orders=[])
        order.payment_method = "cash"

        self.validator.validate(order)

    def test_nonempty_order_without_payment_method_is_rejected(self):
        order = Order(
            id=3,
            customer=self.customer,
            items=[OrderItem(1, "Item", 10.0, 1)],
        )

        with self.assertRaisesRegex(ValueError, "^Order has no payment method$"):
            self.validator.validate(order)


if __name__ == "__main__":
    unittest.main()
