class EmailNotifier:
    def send(self, customer, message: str) -> None:
        print(f"[email] to {customer.email}: {message}")


class SmsNotifier:
    def send(self, customer, message: str) -> None:
        print(f"[sms] to {customer.phone}: {message}")