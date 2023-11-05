A = type("A", (), {})

B = type("B", (A,), {"text": "abc", "double_text": lambda self: self.text * 2})

b = B()
print(b.double_text())  # type: ignore
