import unittest
from unittest.mock import patch

from store.models import Customer, Order, OrderItem
from store.order_service import OrderService


class ExistingCheckoutTests(unittest.TestCase):
    @patch("builtins.print")
    def test_credit_card_checkout_preserves_observable_behavior(self, mock_print):
        customer = Customer(
            id=1,
            name="Test Customer",
            email="test@example.com",
            phone="555-0100",
            credit_card="4111-1111-1111-1111",
        )
        order = Order(
            id=1,
            customer=customer,
            payment_method="credit_card",
            items=[OrderItem(1, "Notebook", 20.0, 1)],
        )

        service = OrderService()
        processed = service.process_order(order)

        output = "\n".join(call.args[0] for call in mock_print.call_args_list)
        self.assertEqual(processed.status, "paid")
        self.assertIs(service.database.load_order(order.id), order)
        self.assertIn("Order 1 total $25.00 (paid_by_credit_card:25.00)", output)
        self.assertIn("[email] to test@example.com", output)
        self.assertIn("[sms] to 555-0100", output)
        self.assertIn("Payment     paid_by_credit_card:25.00", output)


if __name__ == "__main__":
    unittest.main()
