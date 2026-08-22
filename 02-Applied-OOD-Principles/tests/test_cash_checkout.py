import unittest
from unittest.mock import patch

from store.main import build_order_service
from store.models import Customer, Order, OrderItem
from store.payment import CashPaymentHandler


class CashPaymentHandlerTests(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(
            id=1, name="Test Customer", email="test@example.com"
        )
        self.order = Order(id=1, customer=self.customer, payment_method="cash")

    @patch("builtins.print")
    def test_process_returns_paid_by_cash_receipt(self, mock_print):
        receipt = CashPaymentHandler().process(self.order, 42.5)

        self.assertEqual(receipt, "paid_by_cash:42.50")

    @patch("builtins.print")
    def test_console_message_accepts_cash_with_formatted_amount(self, mock_print):
        CashPaymentHandler().process(self.order, 42.5)

        mock_print.assert_called_once_with("[payment] Accepting cash 42.50")

    @patch("builtins.print")
    def test_amount_always_has_two_decimal_places(self, mock_print):
        receipt = CashPaymentHandler().process(self.order, 100)

        self.assertEqual(receipt, "paid_by_cash:100.00")


class CashCheckoutIntegrationTests(unittest.TestCase):
    @patch("builtins.print")
    def test_cash_order_checkout_through_built_service(self, mock_print):
        customer = Customer(
            id=2,
            name="Cash Customer",
            email="cash@example.com",
            phone="555-0242",
        )
        order = Order(
            id=201,
            customer=customer,
            payment_method="cash",
            items=[OrderItem(1, "Notebook", 8.50, 2),
                   OrderItem(2, "Parker Pen", 12.00, 1)],
        )

        service = build_order_service()
        processed = service.process_order(order)

        output = "\n".join(call.args[0] for call in mock_print.call_args_list)
        self.assertEqual(processed.status, "paid")
        self.assertIs(service.database.load_order(order.id), order)
        self.assertIn("paid_by_cash", output)
        self.assertIn("[email] to cash@example.com", output)
        self.assertIn("[sms] to 555-0242", output)
        self.assertIn("Payment     paid_by_cash:34.00", output)


if __name__ == "__main__":
    unittest.main()