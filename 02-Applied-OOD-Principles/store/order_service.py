from store.models import BundleOrder, Order
from store.notification import NotificationService
from store.payment import PaymentProcessor
from store.pricing import DiscountCalculator
from store.storage import MySqlDatabase


class OrderService:
    def __init__(self):
        self.discount_calculator = DiscountCalculator()
        self.payment_processor = PaymentProcessor()
        self.notification = NotificationService()
        self.database = MySqlDatabase()

    def process_order(self, order: Order, notify: bool = True) -> Order:
        # 1. validate
        if not order.items and not isinstance(order, BundleOrder):
            raise ValueError("Order has no items")
        if not order.payment_method:
            raise ValueError("Order has no payment method")

        # 2. price it
        subtotal = order.subtotal
        discount = self.discount_calculator.calculate(order)
        shipping = 5.0 if subtotal < 100 else 0.0
        total = round(subtotal - discount + shipping, 2)

        # 3. charge the customer
        receipt = self.payment_processor.process(order, total)

        # 4. persist
        order.status = "paid"
        self.database.save_order(order)

        # 5. notify
        if notify:
            message = f"Order {order.id} total ${total:.2f} ({receipt})"
            self.notification.send_email(order.customer, message)
            self.notification.send_sms(order.customer, message)

        # 6. print a receipt
        self._print_receipt(order, subtotal, discount, shipping, total, receipt)
        return order

    def _print_receipt(self, order, subtotal, discount, shipping, total, receipt):
        print(f"--- Receipt for order {order.id} ---")
        for item in order.items:
            print(f"  {item.name:20s} x{item.quantity}  ${item.line_total:.2f}")
        print(f"  Subtotal    ${subtotal:.2f}")
        print(f"  Discount   -${discount:.2f}")
        print(f"  Shipping    ${shipping:.2f}")
        print(f"  TOTAL       ${total:.2f}")
        print(f"  Payment     {receipt}")
