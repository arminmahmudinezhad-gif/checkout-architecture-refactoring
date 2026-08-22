import unittest
from unittest.mock import patch

from store.models import Customer, Order
from store.payment import PaymentProcessor


class ExistingPaymentMethodTests(unittest.TestCase):
    @patch("builtins.print")
    def test_process_credit_card_payment(self, mock_print):
        customer = Customer(
            id=1,
            name="Test Customer",
            email="test@example.com",
            credit_card="4111-1111-1111-1111",
        )
        order = Order(id=1, customer=customer, payment_method="credit_card")

        receipt = PaymentProcessor().process(order, 99.99)

        self.assertEqual(receipt, "paid_by_credit_card:99.99")
        mock_print.assert_called_once_with(
            "[payment] Charging card 4111-1111-1111-1111 99.99"
        )

    @patch("builtins.print")
    def test_process_paypal_payment(self, mock_print):
        customer = Customer(
            id=1,
            name="Test Customer",
            email="buyer@example.com",
        )
        order = Order(id=1, customer=customer, payment_method="paypal")

        receipt = PaymentProcessor().process(order, 25.0)

        self.assertEqual(receipt, "paid_by_paypal:25.00")
        mock_print.assert_called_once_with(
            "[payment] Charging PayPal buyer@example.com 25.00"
        )

    @patch("builtins.print")
    def test_process_bitcoin_payment(self, mock_print):
        customer = Customer(
            id=1,
            name="Test Customer",
            email="test@example.com",
            bitcoin_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        )
        order = Order(id=1, customer=customer, payment_method="bitcoin")

        receipt = PaymentProcessor().process(order, 0.5)

        self.assertEqual(receipt, "paid_by_bitcoin:0.50")
        mock_print.assert_called_once_with(
            "[payment] Charging BTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa 0.50"
        )

    def test_process_unknown_payment_raises(self):
        customer = Customer(id=1, name="Test Customer", email="test@example.com")
        order = Order(id=1, customer=customer, payment_method="unknown")

        with self.assertRaises(ValueError) as ctx:
            PaymentProcessor().process(order, 10.0)

        self.assertEqual(str(ctx.exception), "Unknown payment method: 'unknown'")


if __name__ == "__main__":
    unittest.main()