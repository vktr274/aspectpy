class A:
    pass


class B(A):
    text = "abc"

    def double_text(self):
        return self.text * 2


b = B()
print(b.double_text())
