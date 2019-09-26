class A:
    def __init__(self):
        print("I'm A")

    def read_back(list, count):
        if count<0:
            return None
        else:
            for i in range(count):
                yield i

    @property
    def a_property(self):
        return "a_property"

class B(A):
    def __init__(self):
        super().__init__()
        print("I'm B")

class C:
    def __init__(self):
        print("I'm C")

    @property
    def c_property(self):
        return "c_property"

class D(C, A):
    def __init__(self):
        super().__init__()
        A.__init__(self)
        print("I'm D")

a= A()
print(list(a.read_back(-5)))

# a = A()
# print("---")
# b = B()
# print("---")
# c = C()
# print("---")
# d = D()
# print("---")
# print(d.c_property)
# print(d.a_property)
