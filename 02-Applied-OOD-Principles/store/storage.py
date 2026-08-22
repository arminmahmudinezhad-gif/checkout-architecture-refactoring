class MySqlDatabase:
    def __init__(self, connection_string: str = "mysql://localhost/store"):
        self._connection_string = connection_string
        self._orders = {}

    def save_order(self, order) -> None:
        self._orders[order.id] = order

    def load_order(self, order_id: int):
        return self._orders.get(order_id)
