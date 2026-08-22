from store.models import BundleOrder, Customer, Order, OrderItem
from store.notification import EmailNotifier, SmsNotifier
from store.order_service import OrderService
from store.payment import (
    BitcoinPaymentHandler,
    CashPaymentHandler,
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


def build_discount_calculator() -> DiscountCalculator:
    return DiscountCalculator(
        (VipDiscountRule(), BulkDiscountRule(), WelcomeCouponDiscountRule())
    )


def build_payment_processor() -> PaymentProcessor:
    return PaymentProcessor(
        (
            CreditCardPaymentHandler(),
            PayPalPaymentHandler(),
            BitcoinPaymentHandler(),
            CashPaymentHandler(),
        )
    )


def build_notifiers():
    return (EmailNotifier(), SmsNotifier())


def build_order_service() -> OrderService:
    return OrderService(
        payment_processor=build_payment_processor(),
        notifiers=build_notifiers(),
        discount_calculator=build_discount_calculator(),
        database=MySqlDatabase(),
        validator=OrderValidator(),
        receipt_printer=ReceiptPrinter(),
    )


def build_demo_orders():
    vip = Customer(
        id=1, name="Alice", email="alice@example.com",
        phone="555-0100", is_vip=True, credit_card="4111 1111 1111 1111",
    )
    regular = Customer(
        id=2, name="Bob", email="bob@example.com", phone="555-0199",
    )

    laptop = Order(
        id=101, customer=vip, payment_method="credit_card",
        items=[OrderItem(1, "Laptop", 999.99, 1),
               OrderItem(2, "Mouse", 25.00, 1)],
    )

    books = Order(
        id=102, customer=regular, payment_method="paypal",
        items=[OrderItem(3, "Clean Code", 45.00, 2),
               OrderItem(4, "Pragmatic Programmer", 40.00, 2)],
    )

    cash = Order(
        id=104, customer=regular, payment_method="cash",
        items=[OrderItem(5, "Notebook", 8.50, 2),
               OrderItem(6, "Parker Pen", 12.00, 1)],
    )

    bundle = BundleOrder(id=103, customer=vip, orders=[laptop, books])
    bundle.payment_method = "credit_card"
    return laptop, books, cash, bundle


def main() -> None:
    service = build_order_service()
    laptop, books, cash, bundle = build_demo_orders()

    print(">>> Checkout a simple order")
    service.process_order(laptop)

    print("\n>>> Checkout a bundle of two orders")
    service.process_order(bundle)

    print("\n>>> Checkout a cash order")
    service.process_order(cash)


if __name__ == "__main__":
    main()
