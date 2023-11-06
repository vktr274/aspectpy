class A(type):
    def __new__(cls, name, bases, namespace):
        def squared(self):
            return self.num**2

        # Alter class, e.g.
        namespace["num"] = 5
        namespace["squared"] = squared

        return super().__new__(cls, name, bases, namespace)


class B(metaclass=A):
    def __init__(self, num):
        self.num = num


b = B(10)

print(f"b.num from B.__init__ is {b.num}")
print(f"Class B has a squared method outputting {b.squared()}")  # type: ignore
