from abc import ABCMeta, abstractmethod


class SaferPaymentMethod:
    def __init__(self, new_cls: type, change: bool):
        self.new_cls = new_cls
        self.change = change

    def __call__(self, cls: type):
        def wrapper(*args, **kwargs):
            if not self.change:
                return cls(*args, **kwargs)
            return self.new_cls(*args, **kwargs)

        return wrapper


class Payment(metaclass=ABCMeta):
    @abstractmethod
    def pay(self, amount: int):
        pass

    @abstractmethod
    def refund(self, amount: int):
        pass


# Cannot be a subclass of OnlineCard due to Python's MRO
class PayPal(Payment):
    def pay(self, amount: int):
        print(f"PayPal payment of {amount}$ processed.")

    def refund(self, amount: int):
        print(f"PayPal refund of {amount}$ processed.")


@SaferPaymentMethod(PayPal, change=True)
class OnlineCard(Payment):
    def pay(self, amount: int):
        print(f"Online card payment of {amount}$ processed.")

    def refund(self, amount: int):
        print(f"Online card refund of {amount}$ processed.")


online_card = OnlineCard()

online_card.pay(100)
online_card.refund(100)

print(online_card.__class__.__name__)
