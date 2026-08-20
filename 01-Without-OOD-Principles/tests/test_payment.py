import unittest
from unittest.mock import patch

from store.models import Customer, Order
from store.payment import PaymentProcessor


class PaymentProcessorCashTests(unittest.TestCase):
    @patch("builtins.print")
    def test_process_cash_payment(self, mock_print):
        customer = Customer(id=1, name="Test Customer", email="test@example.com")
        order = Order(id=1, customer=customer, payment_method="cash")

        receipt = PaymentProcessor().process(order, 42.5)

        self.assertEqual(receipt, "paid_by_cash:42.50")
        mock_print.assert_called_once_with("[payment] Accepting cash 42.50")


if __name__ == "__main__":
    unittest.main()
