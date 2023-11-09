from abc import ABCMeta, abstractmethod


registry = {}


def register(cls):
    registry[cls.__name__] = cls
    return cls


def safer_payment_method(name, change=False):
    def decorator(cls):
        class Wrapper(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if change:
                    if name not in registry:
                        raise ValueError(f"Class {name} not found in registry.")
                    self.__class__ = registry[name]
                else:
                    self.__class__ = cls

        return Wrapper

    return decorator


class Payment(metaclass=ABCMeta):
    @abstractmethod
    def pay(self, amount: int):
        pass

    @abstractmethod
    def refund(self, amount: int):
        pass


@safer_payment_method("PayPal", change=True)
class OnlineCard(Payment):
    def pay(self, amount: int):
        print(f"Online card payment of {amount}$ processed.")

    def refund(self, amount: int):
        print(f"Online card refund of {amount}$ processed.")


@register
class PayPal(OnlineCard):
    def pay(self, amount: int):
        print(f"PayPal payment of {2 * amount}$ processed.")

    def refund(self, amount: int):
        print(f"PayPal refund of {2 * amount}$ processed.")


online_card = OnlineCard()

online_card.pay(100)
online_card.refund(100)

print(online_card.__class__)
