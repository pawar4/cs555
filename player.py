import socket

class Player:

    def __init__(self, _group_size) -> None:
        self.group_size = _group_size

    def group_add(self, x, y):
        return (x + y) % self.group_size

    def group_mul(self, x, y):
        return (x * y) % self.group_size

    def group_div(self, x, y):
        return x * self.group_inv(y)

    def group_inv(self, x):
        return pow(x, self.group_size - 2, self.group_size)


