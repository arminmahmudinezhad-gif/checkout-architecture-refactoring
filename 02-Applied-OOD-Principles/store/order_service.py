from collections.abc import Iterable

from store.contracts import Notifier, OrderRepository, PricingCalculator
from store.models import Order
from store.payment import PaymentProcessor
from store.receipt import ReceiptPrinter
from store.validation import OrderValidator


class OrderService:
    def __init__(
        self,
        payment_processor: PaymentProcessor,
        notifiers: Iterable[Notifier],
        discount_calculator: PricingCalculator,
        database: OrderRepository,
        validator: OrderValidator,
        receipt_printer: ReceiptPrinter,
    ) -> None:
        self.payment_processor = payment_processor
        self.notifiers = tuple(notifiers)
        self.discount_calculator = discount_calculator
        self.database = database
        self.validator = validator
        self.receipt_printer = receipt_printer

    def process_order(self, order: Order, notify: bool = True) -> Order:
        self.validator.validate(order)

        subtotal = order.subtotal
        discount = self.discount_calculator.calculate(order)
        shipping = 5.0 if subtotal < 100 else 0.0
        total = round(subtotal - discount + shipping, 2)

        receipt = self.payment_processor.process(order, total)

        order.status = "paid"
        self.database.save_order(order)

        if notify:
            message = f"Order {order.id} total ${total:.2f} ({receipt})"
            for notifier in self.notifiers:
                notifier.send(order.customer, message)

        self.receipt_printer.print(
            order, subtotal, discount, shipping, total, receipt
        )
        return order