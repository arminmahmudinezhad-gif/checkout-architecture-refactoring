from store.models import Order


class ReceiptPrinter:
    def print(
        self,
        order: Order,
        subtotal: float,
        discount: float,
        shipping: float,
        total: float,
        receipt: str,
    ) -> None:
        print(f"--- Receipt for order {order.id} ---")
        for item in order.items:
            print(f"  {item.name:20s} x{item.quantity}  ${item.line_total:.2f}")
        print(f"  Subtotal    ${subtotal:.2f}")
        print(f"  Discount   -${discount:.2f}")
        print(f"  Shipping    ${shipping:.2f}")
        print(f"  TOTAL       ${total:.2f}")
        print(f"  Payment     {receipt}")