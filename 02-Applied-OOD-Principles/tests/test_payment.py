import unittest
from unittest.mock import patch

from store.main import build_payment_processor
from store.models import Customer, Order
from store.payment import PaymentProcessor


class ExistingPaymentMethodTests(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(
            id=1,
            name="Test Customer",
            email="buyer@example.com",
            credit_card="4111-1111-1111-1111",
            bitcoin_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        )

    @patch("builtins.print")
    def test_process_credit_card_payment(self, mock_print):
        order = Order(
            id=1, customer=self.customer, payment_method="credit_card"
        )

        receipt = build_payment_processor().process(order, 99.99)

        self.assertEqual(receipt, "paid_by_credit_card:99.99")
        mock_print.assert_called_once_with(
            "[payment] Charging card 4111-1111-1111-1111 99.99"
        )

    @patch("builtins.print")
    def test_process_paypal_payment(self, mock_print):
        order = Order(id=1, customer=self.customer, payment_method="paypal")

        receipt = build_payment_processor().process(order, 25.0)

        self.assertEqual(receipt, "paid_by_paypal:25.00")
        mock_print.assert_called_once_with(
            "[payment] Charging PayPal buyer@example.com 25.00"
        )

    @patch("builtins.print")
    def test_process_bitcoin_payment(self, mock_print):
        order = Order(id=1, customer=self.customer, payment_method="bitcoin")

        receipt = build_payment_processor().process(order, 0.5)

        self.assertEqual(receipt, "paid_by_bitcoin:0.50")
        mock_print.assert_called_once_with(
            "[payment] Charging BTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa 0.50"
        )

    @patch("builtins.print")
    def test_process_cash_payment(self, mock_print):
        order = Order(id=1, customer=self.customer, payment_method="cash")

        receipt = build_payment_processor().process(order, 20.0)

        self.assertEqual(receipt, "paid_by_cash:20.00")
        mock_print.assert_called_once_with("[payment] Accepting cash 20.00")

    def test_process_unknown_payment_raises(self):
        order = Order(id=1, customer=self.customer, payment_method="unknown")

        with self.assertRaises(ValueError) as ctx:
            build_payment_processor().process(order, 10.0)

        self.assertEqual(str(ctx.exception), "Unknown payment method: 'unknown'")

    def test_dispatches_to_an_injected_handler(self):
        class TestPaymentHandler:
            method = "test_method"

            def process(self, order, amount):
                return f"test_receipt:{order.id}:{amount:.2f}"

        order = Order(id=7, customer=self.customer, payment_method="test_method")
        processor = PaymentProcessor([TestPaymentHandler()])

        receipt = processor.process(order, 12.5)

        self.assertEqual(receipt, "test_receipt:7:12.50")


if __name__ == "__main__":
    unittest.main()
