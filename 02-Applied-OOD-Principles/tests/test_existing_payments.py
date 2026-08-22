import unittest
from unittest.mock import patch

from store.models import Customer, Order, OrderItem
from store.notification import EmailNotifier, SmsNotifier
from store.order_service import OrderService
from store.payment import (
    BitcoinPaymentHandler,
    CreditCardPaymentHandler,
    PayPalPaymentHandler,
    PaymentProcessor,
)
from store.pricing import (
    BulkDiscountRule,
    DiscountCalculator,
    VipDiscountRule,
    WelcomeCouponDiscountRule,
)
from store.receipt import ReceiptPrinter
from store.storage import MySqlDatabase
from store.validation import OrderValidator


def build_service() -> OrderService:
    return OrderService(
        payment_processor=PaymentProcessor(
            (
                CreditCardPaymentHandler(),
                PayPalPaymentHandler(),
                BitcoinPaymentHandler(),
            )
        ),
        notifiers=(EmailNotifier(), SmsNotifier()),
        discount_calculator=DiscountCalculator(
            (VipDiscountRule(), BulkDiscountRule(), WelcomeCouponDiscountRule())
        ),
        database=MySqlDatabase(),
        validator=OrderValidator(),
        receipt_printer=ReceiptPrinter(),
    )


class ExistingPaymentCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(
            id=1,
            name="Test Customer",
            email="buyer@example.com",
            phone="555-0100",
            credit_card="4111-1111-1111-1111",
        )

    @patch("builtins.print")
    def test_credit_card_order_checkout(self, mock_print):
        order = Order(
            id=1,
            customer=self.customer,
            payment_method="credit_card",
            items=[OrderItem(1, "Laptop", 500.0, 1)],
        )

        service = build_service()
        processed = service.process_order(order)

        output = "\n".join(call.args[0] for call in mock_print.call_args_list)
        self.assertEqual(processed.status, "paid")
        self.assertIn("paid_by_credit_card:500.00", output)

    @patch("builtins.print")
    def test_paypal_order_checkout(self, mock_print):
        order = Order(
            id=2,
            customer=self.customer,
            payment_method="paypal",
            items=[OrderItem(2, "Notebook", 10.0, 1)],
        )

        service = build_service()
        processed = service.process_order(order)

        output = "\n".join(call.args[0] for call in mock_print.call_args_list)
        self.assertEqual(processed.status, "paid")
        self.assertIn("paid_by_paypal:15.00", output)

    @patch("builtins.print")
    def test_bitcoin_order_checkout(self, mock_print):
        order = Order(
            id=3,
            customer=self.customer,
            payment_method="bitcoin",
            items=[OrderItem(3, "Book", 20.0, 1)],
        )

        service = build_service()
        processed = service.process_order(order)

        output = "\n".join(call.args[0] for call in mock_print.call_args_list)
        self.assertEqual(processed.status, "paid")
        self.assertIn("paid_by_bitcoin:25.00", output)

    def test_unknown_payment_method_raises(self):
        order = Order(
            id=4,
            customer=self.customer,
            payment_method="unknown",
            items=[OrderItem(4, "Mug", 5.0, 1)],
        )

        service = build_service()
        with self.assertRaises(ValueError) as ctx:
            service.process_order(order)

        self.assertEqual(str(ctx.exception), "Unknown payment method: 'unknown'")


if __name__ == "__main__":
    unittest.main()