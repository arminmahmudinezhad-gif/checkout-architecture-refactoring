import unittest
from unittest.mock import patch

from store.main import build_demo_orders, build_order_service
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

        service = build_service()
        processed = service.process_order(order)

        output = "\n".join(call.args[0] for call in mock_print.call_args_list)
        self.assertEqual(processed.status, "paid")
        self.assertIs(service.database.load_order(order.id), order)
        self.assertIn("Order 1 total $25.00 (paid_by_credit_card:25.00)", output)
        self.assertIn("[email] to test@example.com", output)
        self.assertIn("[sms] to 555-0100", output)
        self.assertIn("Payment     paid_by_credit_card:25.00", output)

    @patch("builtins.print")
    def test_notify_false_skips_notifications_but_completes_checkout(self, mock_print):
        customer = Customer(
            id=2,
            name="No Notification Customer",
            email="quiet@example.com",
            phone="555-0200",
        )
        order = Order(
            id=2,
            customer=customer,
            payment_method="cash",
            items=[OrderItem(1, "Notebook", 20.0, 1)],
        )
        service = build_order_service()

        processed = service.process_order(order, notify=False)

        output = "\n".join(call.args[0] for call in mock_print.call_args_list)
        self.assertEqual(processed.status, "paid")
        self.assertIs(service.database.load_order(order.id), order)
        self.assertIn("[payment] Accepting cash 25.00", output)
        self.assertIn("Payment     paid_by_cash:25.00", output)
        self.assertNotIn("[email]", output)
        self.assertNotIn("[sms]", output)

    @patch("builtins.print")
    def test_bundle_order_checkout_through_built_service(self, mock_print):
        _, _, _, bundle = build_demo_orders()
        service = build_order_service()

        processed = service.process_order(bundle)

        output = "\n".join(call.args[0] for call in mock_print.call_args_list)
        self.assertEqual(processed.status, "paid")
        self.assertIs(service.database.load_order(bundle.id), bundle)
        self.assertIn("paid_by_credit_card:5.00", output)
        self.assertIn("[email] to alice@example.com", output)
        self.assertIn("[sms] to 555-0100", output)
        self.assertIn("--- Receipt for order 103 ---", output)
        self.assertIn("Payment     paid_by_credit_card:5.00", output)


if __name__ == "__main__":
    unittest.main()
