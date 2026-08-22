from dataclasses import dataclass, field
from typing import List


@dataclass
class Customer:
    id: int
    name: str
    email: str
    phone: str = ""
    is_vip: bool = False
    address: str = ""
    credit_card: str = ""
    bitcoin_address: str = ""


@dataclass
class OrderItem:
    product_id: int
    name: str
    price: float
    quantity: int

    @property
    def line_total(self) -> float:
        return self.price * self.quantity


@dataclass
class Order:
    id: int
    customer: Customer
    items: List[OrderItem] = field(default_factory=list)
    status: str = "pending"
    payment_method: str = ""
    coupons: List[str] = field(default_factory=list)

    @property
    def subtotal(self) -> float:
        return sum(item.line_total for item in self.items)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)


class BundleOrder(Order):
    def __init__(self, id: int, customer: Customer, orders: List[Order]):
        super().__init__(id=id, customer=customer, items=[])
        self.orders = orders
