import unittest
from unittest.mock import patch

from store.models import Customer, Order, OrderItem
from store.order_service import OrderService


class CashCheckoutIntegrationTests(unittest.TestCase):
    @patch("store.notification.print")
    @patch("builtins.print")
    def test_cash_order_is_marked_paid(self, mock_print, mock_notification_print):
        customer = Customer(id=1, name="Test Customer", email="test@example.com")
        order = Order(
            id=1,
            customer=customer,
            payment_method="cash",
            items=[OrderItem(1, "Notebook", 8.50, 2)],
        )

        processed = OrderService().process_order(order)

        self.assertEqual(processed.status, "paid")

    @patch("builtins.print")
    def test_cash_receipt_appears_in_checkout_output(self, mock_print):
        customer = Customer(id=1, name="Test Customer", email="test@example.com")
        order = Order(
            id=1,
            customer=customer,
            payment_method="cash",
            items=[OrderItem(1, "Notebook", 8.50, 2)],
        )

        OrderService().process_order(order)

        printed_text = [call.args[0] for call in mock_print.call_args_list]
        checkout_output = "\n".join(printed_text)
        self.assertIn("paid_by_cash", checkout_output)


if __name__ == "__main__":
    unittest.main()